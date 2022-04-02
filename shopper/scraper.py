"""A Simple Web Scraper Module"""

import requests
from urllib3 import Retry
from loguru import logger
from shopper.utils import IntConverter, StrAlnumSpaceConverter, MySQLHandle

logger.add("logs/default.log")

# Create directly in MySQL
# CREATE TABLE products
# (
#     userid int NOT NULL,
#     sku varchar(15) NOT NULL,
#     name varchar(64) NOT NULL,
#     store char(3) NOT NULL,
#     track int NOT NULL DEFAULT 1,
#     PRIMARY KEY (userid, sku, store)
# );

# Create directly in MySQL
# CREATE TABLE inventory
# (
#     userid int NOT NULL,
#     sku varchar(15) NOT NULL,
#     quantity int NOT NULL,
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     store_name varchar(48) NOT NULL,
#     PRIMARY KEY (userid, sku, store, store_id)
# );


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

    @staticmethod
    def list_all_products(userid, track=False):
        if track:
            data = ScraperMySQLInterface.list_all_track_products(userid)
        else:
            data = ScraperMySQLInterface.list_all_products(userid)
        if data is None:
            return None

        result = []
        for sku, name, store, track in data:
            result.append(
                {"sku": sku,
                 "name": name,
                 "store": store,
                 "track": track}
            )
        return result

    @staticmethod
    def update_product(userid, sku, store, track):
        return ScraperMySQLInterface.update_product(userid, sku, store, track)

    @staticmethod
    def add_product(userid, sku, name, store):
        name = StrAlnumSpaceConverter(name).value
        return ScraperMySQLInterface.add_product(userid, sku, name, store)

    @staticmethod
    def delete_all_inventory(userid):
        ScraperMySQLInterface.delete_all_inventory(userid)

    @staticmethod
    def list_all_inventory(userid, zipcode):
        if not zipcode.strip().isdigit() or len(zipcode) != 5:
            return None

        ScraperBase.delete_all_inventory(userid)
        products = ScraperBase.list_all_products(userid, track=True)
        names = dict()
        for product in products:
            sku = product.get("sku")
            name = product.get("name")
            store = product.get("store")
            names[sku, store] = name
            if store == "tgt":
                ScraperTarget().get_qty_by_sku_zipcode(userid, sku, zipcode)

        inventory = ScraperMySQLInterface.list_all_inventory(userid)
        if inventory is None:
            return None

        prev = (None, None)
        result = []
        for sku, quantity, store, store_name in inventory:
            if (store, store_name) != prev:
                result.append({
                    "store": store,
                    "name": store_name,
                    "products": [{
                        "sku": sku,
                        "name": names[sku, store],
                        "quantity": quantity
                    }]
                })
            else:
                result[-1]["products"].append({
                    "sku": sku,
                    "name": names[sku, store],
                    "quantity": quantity
                })
            prev = (store, store_name)
        return result


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

        result = False
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
        if info:
            result = ScraperMySQLInterface.add_inventory(info)
        return result


class ScraperDataInterface:
    """Data interface for Scraper base class"""

    @classmethod
    def add_product(cls, userid, sku, name, store):
        pass

    @classmethod
    def list_all_products(cls, userid):
        pass

    @classmethod
    def list_all_track_products(cls, userid):
        pass

    @classmethod
    def update_product(cls, userid, sku, store, track):
        pass

    @classmethod
    def add_inventory(cls, data):
        pass

    @classmethod
    def delete_all_inventory(cls, userid):
        pass

    @classmethod
    def list_all_inventory(cls, userid):
        pass


class ScraperMySQLInterface(ScraperDataInterface):
    """Data interface for Scraper implemented with MySQL"""

    @classmethod
    def add_product(cls, userid, sku, name, store):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO products (userid, sku, name, store)"
                    "VALUES (%s, %s, %s, %s)"
                )
                result = db.run(query, (userid, sku, name, store), commit=True)
            else:
                result = None
                print("Server Error")
        return result

    @classmethod
    def list_all_products(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT sku, name, store, track FROM products WHERE userid = %s"
                result = db.run(query, (userid,))
            else:
                result = None
                print("Server Error")
        return result

    @classmethod
    def list_all_track_products(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT sku, name, store, track FROM products WHERE userid = %s AND track = 1"
                result = db.run(query, (userid,))
            else:
                result = None
                print("Server Error")
        return result

    @classmethod
    def update_product(cls, userid, sku, store, track):
        with MySQLHandle() as db:
            if db.conn:
                query = "UPDATE products SET track = %s WHERE userid = %s AND sku = %s AND store = %s"
                result = db.run(query, (track, userid, sku, store), commit=True)
            else:
                result = None
                print("Server Error")
        return result

    @classmethod
    def add_inventory(cls, data):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO inventory (userid, sku, quantity, store, store_id, store_name)"
                    "VALUES (%s, %s, %s, %s, %s, %s)"
                )
                result = db.run(query, data, commit=True, many=True)
            else:
                result = None
                print("Server Error")
        return result

    @classmethod
    def delete_all_inventory(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "DELETE FROM inventory WHERE userid = %s"
                result = db.run(query, (userid,), commit=True)
            else:
                result = None
                print("Server Error")
        return result

    @classmethod
    def list_all_inventory(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "SELECT sku, quantity, store, store_name FROM inventory WHERE userid = %s "
                    "ORDER BY store, store_name, sku"
                )
                result = db.run(query, (userid,))
            else:
                result = None
                print("Server Error")
        return result
