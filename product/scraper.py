"""A Simple Web Scraper Module"""

from django.conf import settings
import importlib.util
from loguru import logger
import os
import requests
from urllib3 import Retry

logger.add("logs/default.log")

spec = importlib.util.spec_from_file_location("utils",
                                              os.path.join(settings.BASE_DIR,
                                                           "shopper/utils.py"))
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


class AutoAdapter(requests.adapters.HTTPAdapter):
    """HTTPAdapter with timeout and auto retry"""
    
    def __init__(self, *args, **kwargs):
        """Set timeout as 3 seconds and try at most 3 times unless overwritten
        """
        
        # default timeout: 3 seconds
        self._timeout = 3
        # default retry: 3 times
        self._retry = Retry(
            total=3,
            status_forcelist=[413, 429, 500, 502, 503, 504],
            backoff_factor=0.5
        )

        # HTTPAdapter does not use "timeout" as argument
        # delete to avoid repeated argument when overwriting default timeout
        if "timeout" in kwargs:
            self._timeout = kwargs["timeout"]
            del kwargs["timeout"]
        
        # HTTPAdapter uses "max_retries" as argument
        # set to default retry if not assigned
        if kwargs.get("max_retries") is None:
            kwargs["max_retries"] = self._retry

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
            kwargs["timeout"] = self._timeout
        return super().send(request, **kwargs)


class ScraperBase:
    """Scraper base class"""
    
    # change with AutoAdapter(timeout=3, max_retries=3) if needed
    _adapter = AutoAdapter()
    
    def __init__(self, url=None):
        """

        Args:
            url (str, optional): url. Defaults to None.
        """
        self._url = url
        self._response = None

    def _download(self):
        """Download and store response
        """
        if self._url is None:
            return

        try:
            with requests.Session() as session:
                session.mount("https://", self._adapter)
                session.mount("http://", self._adapter)
                rsp = session.get(self._url)
        except requests.exceptions.ConnectionError:
            logger.debug(f"{type(self).__name__} : {self._url}")
        except:
            logger.error(f"{type(self).__name__} : {self._url}")
        else:
            self._response = rsp


class ScraperTarget(ScraperBase):
    """Scraper for Target"""
    
    def search_product(self, keyword):
        if not keyword.strip().isdigit() or len(keyword) not in (8, 9, 12, 13):
            return None

        self._url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v1?"
            "key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB"
            f"&keyword={keyword}&page=/s/{keyword}&pricing_store_id=1296"
            "&visitor_id=017A6DC6EE8F1211A79B8E2D32284BE2"
        )
        self._download()
        info = dict()
        if self._response is not None and self._response.status_code == 200:
            try:
                data = self._response.json()["data"]["search"]["products"][0]
                sku = utils.IntConverter(data["tcin"]).value
                name = utils.StrAlnumSpaceConverter(data["item"]["product_description"]["title"]).value[:64]
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

        self._url = (
            "https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?"
            f"key=9f36aeafbe60771e321a7cc95a78140772ab3e96&tcin={sku}&is_bot=false"
            "&pricing_store_id=1296"
        )
        self._download()
        info = dict()
        if self._response is not None and self._response.status_code == 200:
            print(self._response)
            try:
                data = self._response.json()["data"]["product"]["item"]
                name = data["product_description"]["title"]
                info["name"] = name
            except Exception:
                logger.exception(f"{type(self).__name__} : {sku}")
        return info

    def get_qty_by_sku_zipcode(self, sku, zipcode):
        # "81911643", "12011"
        if not sku.isdigit() or len(sku) != 8 or not zipcode.isdigit() or len(zipcode) != 5:
            return None

        self._url = (
            "https://redsky.target.com/redsky_aggregations/v1/web_platform/fiats_v1?"
            f"key=9f36aeafbe60771e321a7cc95a78140772ab3e96&tcin={sku}&nearby={zipcode}"
            "&radius=50&limit=20&include_only_available_stores=true&requested_quantity=0"
        )
        self._download()

        info = []
        if self._response is not None and self._response.status_code == 200:
            try:
                for location in self._response.json()["data"]["fulfillment_fiats"]["locations"]:
                    store_id = utils.StrAlnumSpaceConverter(str(location["store"]["store_id"])).value
                    # store_name = utils.StrAlnumSpaceConverter(location["store"]["location_name"]).value
                    quantity = utils.IntConverter(location["location_available_to_promise_quantity"]).value
                    info.append((sku, quantity, "tgt", store_id))
            except Exception:
                logger.exception(f"{type(self).__name__} : {sku} - {zipcode}")
        return info

    def get_stores_by_zipcode(self, zipcode):
        self._url = (
            "https://api.target.com/location_proximities/v1/nearby_locations?limit=20"
            f"&unit=mile&within=100&place={zipcode}"
            "&type=store&key=8df66ea1e1fc070a6ea99e942431c9cd67a80f02"
        )
        self._download()
        info = []
        if self._response is not None and self._response.status_code == 200:
            try:
                for location in self._response.json()["locations"]:
                    store_id = utils.StrAlnumSpaceConverter(str(location["location_id"])).value
                    name = utils.StrAlnumSpaceConverter(location["location_names"][0]["name"]).value
                    address = utils.StrAlnumSpaceConverter(location["address"]["address_line1"]).value
                    city = utils.StrAlnumSpaceConverter(location["address"]["city"]).value
                    state = utils.StrAlnumSpaceConverter(location["address"]["state"]).value
                    postal_code = utils.StrAlnumSpaceConverter(location["address"]["postal_code"].split("-")[0]).value
                    latitude = location["geographic_specifications"]["latitude"]
                    longitude = location["geographic_specifications"]["longitude"]
                    info.append(("tgt", store_id, name, address, city, state, postal_code, latitude, longitude))
            except Exception:
                logger.exception(f"{type(self).__name__} : {zipcode}")
        return info
