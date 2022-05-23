"""Product Module"""

from product.data import ProductMySQLInterface
from product.utils import StrAlnumSpaceConverter, Downloader
from product import tasks
import json
from loguru import logger


logger.add("logs/default.log")


class Product:
    """Product base class"""
    
    @staticmethod
    def list_all_products(userid):
        data = ProductMySQLInterface.list_all_products(userid)
        if data is None:
            return None

        return json.loads(data[0][0]) if data and data[0][0] else []

    @staticmethod
    def update_product(userid, sku, store, track):
        return ProductMySQLInterface.update_product(userid, sku, store, track)

    @staticmethod
    def search_product(store, keyword):
        info = dict()
        if store == "tgt":
            # PORTS: - 8001:8000 enables access 127.0.0.1:8001/X in
            # browser. But inter-container communication uses 8000.
            downloader = Downloader(
                "http://scraper-web:8000/scraper/"
                f"target/product/{keyword}/"
            )
            resp = downloader.response
            if resp and resp.status_code == 200:
                try:
                    info = resp.json().get("info")
                except Exception:
                    logger.exception(f"search_product : {keyword}")
                if info is None:
                    info = dict()
        return info

    @staticmethod
    def add_product(userid, sku, name, store):
        name = StrAlnumSpaceConverter(name).value
        return ProductMySQLInterface.add_product(userid, sku, name, store)

    @staticmethod
    def get_zipcode(userid):
        return ProductMySQLInterface.get_zipcode(userid)

    @staticmethod
    def update_zipcode(userid, zipcode):
        # update zipcode asynchronously
        tasks.update_zipcode.delay(userid, zipcode)

    @staticmethod
    def _delete_all_inventory(userid):
        ProductMySQLInterface.delete_all_inventory(userid)

    @staticmethod
    def _get_quantity(count, sku, store, zipcode):
        # get quantity synchronously and locally
        info = tasks.get_quantity_from_store.run(count, sku, store, zipcode)
        tasks.add_quantity_to_db.run(info)

    @staticmethod
    def _get_store_info(store, zipcode):
        print(f"Getting store info for {store} around {zipcode} ...")
        if store == "tgt":
            store_info = None
            downloader = Downloader(
                "http://scraper-web:8000/scraper/"
                f"target/store/{zipcode}/"
            )
            resp = downloader.response
            if resp and resp.status_code == 200:
                try:
                    store_info = resp.json().get("info")
                except Exception:
                    logger.exception(f"get_store_info : {zipcode}")
                if store_info is None:
                    store_info = dict()
            if store_info is None:
                return
            ProductMySQLInterface.add_stores(store_info)
            if len(store_info) == 20:
                data = []
                for item in store_info:
                    store_id = item[1]
                    data.append((store, zipcode, store_id))
                ProductMySQLInterface.add_zipcode_stores_mapping(data)

    @staticmethod
    def list_all_inventory(userid, zipcode):
        data = ProductMySQLInterface.list_all_track_products(userid)
        if data is None:
            return None

        products = json.loads(data[0][0]) if data and data[0][0] else []

        # get store info ready
        stores_to_check = set()
        for product in products:
            store = product.get("store")
            stores_to_check.add(store)
        for store in stores_to_check:
            # zipcode_stores_mapping not existing
            if not ProductMySQLInterface.get_mapping_by_zipcode_store(store, zipcode):
                Product._get_store_info(store, zipcode)

        # get inventory ready
        for product in products:
            sku = product.get("sku")
            store = product.get("store")
            # count of stores with the latest quantity
            count = 0
            data = ProductMySQLInterface.count_store_with_latest(sku, store, zipcode)
            if data:
                count = data[0][0]
            Product._get_quantity(count, sku, store, zipcode)

        data = ProductMySQLInterface.list_all_inventory(userid, zipcode)
        if data is None:
            return None
        return json.loads(data[0][0]) if data and data[0][0] else []

    @staticmethod
    def preload(userid):
        # refresh cache asynchronously
        tasks.preload.delay(userid)
