"""Product Module"""

from django.conf import settings
from product.data import ProductMySQLInterface
from product.scraper import ScraperTarget
from product import tasks
import importlib.util
import json
from loguru import logger
import os


logger.add("logs/default.log")

spec = importlib.util.spec_from_file_location("utils",
                                              os.path.join(settings.BASE_DIR,
                                                           "shopper/utils.py"))
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


class Product:
    """Product base class"""
    
    @staticmethod
    def list_all_products(userid):
        data = ProductMySQLInterface.list_all_products(userid)
        if data is None:
            return None

        return json.loads(data[0][0]) if data else []

    @staticmethod
    def update_product(userid, sku, store, track):
        return ProductMySQLInterface.update_product(userid, sku, store, track)

    @staticmethod
    def search_product(store, keyword):
        if store == "tgt":
            return ScraperTarget().search_product(keyword)
        return dict()

    @staticmethod
    def add_product(userid, sku, name, store):
        name = utils.StrAlnumSpaceConverter(name).value
        return ProductMySQLInterface.add_product(userid, sku, name, store)

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
            store_info = ScraperTarget().get_stores_by_zipcode(zipcode)
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

        products = json.loads(data[0][0]) if data else []

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
        return json.loads(data[0][0]) if data else []

    @staticmethod
    def preload(userid):
        # refresh cache asynchronously
        tasks.preload.delay(userid)
