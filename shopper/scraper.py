"""A Simple Web Scraper Module"""

import requests
from urllib3 import Retry
from loguru import logger
from shopper.utils import IntConverter, StrAlnumSpaceConverter

logger.add("logs/default.log")


class AutoAdapter(requests.adapters.HTTPAdapter):
    """HTTPAdapter with timeout and auto retry"""
    
    def __init__(self, *args, **kwargs):
        """Set timeout as 3 seconds and try at most 3 times unless overwritten
        """
        
        # default timeout: 3 seconds
        self.timeout = 3
        # HTTPAdapter does not use "timeout" as argument
        # delete to avoid repeated argument when overwriting default timeout
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        
        # default retry: 3 times
        if kwargs.get("max_retries") is None:
            kwargs["max_retries"] = Retry(
                total=3,
                status_forcelist=[413, 429, 500, 502, 503, 504],
                backoff_factor=0.5
            )
        super().__init__(*args, **kwargs)
    
    def send(self, request, **kwargs):
        """Send request with timeout

        Args:
            request (type): request object

        Returns:
            type: response object
        """
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class ScraperBase:
    """Scraper base class"""
    
    # change with AutoAdapter(timeout=3, max_retries=3) if needed
    adapter = AutoAdapter()
    
    def __init__(self, url=None):
        """

        Args:
            url (str, optional): url. Defaults to None.
        """
        self.url = url
        self.response = None

    def _download(self):
        """Download and store response
        """
        if self.url is None:
            return

        try:
            with requests.Session() as session:
                session.mount("https://", self.adapter)
                session.mount("http://", self.adapter)
                rsp = session.get(self.url)
        except requests.exceptions.ConnectionError:
            logger.debug(f"{type(self).__name__} : {self.url}")
        except:
            logger.error(f"{type(self).__name__} : {self.url}")
        else:
            self.response = rsp


class ScraperTarget(ScraperBase):
    """Scraper for Target"""
    
    def search_product(self, keyword):
        if not keyword.strip().isdigit() or len(keyword) not in (8, 9, 12, 13):
            return None

        self.url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1?"
            "key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB"
            f"&keyword={keyword}&page=/s/{keyword}&pricing_store_id=1296"
            "&visitor_id=017A6DC6EE8F1211A79B8E2D32284BE2"
        )
        self._download()
        info = dict()
        if self.response is not None and self.response.status_code == 200:
            try:
                data = self.response.json()["data"]["search"]["products"][0]
                sku = IntConverter(data["tcin"]).value
                name = StrAlnumSpaceConverter(data["item"]["product_description"]["title"]).value[:64]
                info = {"sku": sku, "name": name}
            except IndexError:
                pass
            except Exception:
                logger.exception(f"{type(self).__name__} : {keyword}")
        return info

    def get_product_info_by_sku(self, sku):
        # "81911643"
        if not sku.strip().isdigit() or len(sku) != 8:
            return None

        self.url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?"
            f"key=9f36aeafbe60771e321a7cc95a78140772ab3e96&tcin={sku}&is_bot=false"
            "&pricing_store_id=1296"
        )
        self._download()
        info = dict()
        if self.response is not None and self.response.status_code == 200:
            print(self.response)
            try:
                data = self.response.json()["data"]["product"]["item"]
                name = data["product_description"]["title"]
                info["name"] = name
            except Exception:
                logger.exception(f"{type(self).__name__} : {sku}")
        return info

    def get_qty_by_sku_zipcode(self, userid, sku, zipcode):
        # "81911643", "12011"
        if not sku.isdigit() or len(sku) != 8 or not zipcode.isdigit() or len(zipcode) != 5:
            return None

        self.url = (
            "https://redsky.target.com/redsky_aggregations/v1/web_platform/fiats_v1?"
            f"key=9f36aeafbe60771e321a7cc95a78140772ab3e96&tcin={sku}&nearby={zipcode}"
            "&radius=50&limit=20&include_only_available_stores=true&requested_quantity=1"
        )
        self._download()

        info = []
        if self.response is not None and self.response.status_code == 200:
            try:
                for location in self.response.json()["data"]["fulfillment_fiats"]["locations"]:
                    store_id = StrAlnumSpaceConverter(str(location["store"]["store_id"])).value
                    store_name = StrAlnumSpaceConverter(location["store"]["location_name"]).value
                    quantity = IntConverter(location["location_available_to_promise_quantity"]).value
                    info.append((userid, sku, quantity, "tgt", store_id, store_name))
            except Exception:
                logger.exception(f"{type(self).__name__} : {sku} - {zipcode}")
        return info
