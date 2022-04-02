"""Shopper Module"""

from shopper.scraper import ScraperTarget
from shopper.utils import StrAlnumSpaceConverter, MySQLHandle
from loguru import logger

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


class Shopper:
    """Shopper base class"""

    @staticmethod
    def list_all_products(userid, track=False):
        if track:
            data = ShopperMySQLInterface.list_all_track_products(userid)
        else:
            data = ShopperMySQLInterface.list_all_products(userid)
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
        return ShopperMySQLInterface.update_product(userid, sku, store, track)

    @staticmethod
    def add_product(userid, sku, name, store):
        name = StrAlnumSpaceConverter(name).value
        return ShopperMySQLInterface.add_product(userid, sku, name, store)

    @staticmethod
    def delete_all_inventory(userid):
        ShopperMySQLInterface.delete_all_inventory(userid)

    @staticmethod
    def list_all_inventory(userid, zipcode):
        products = Shopper.list_all_products(userid, track=True)
        names = dict()
        for product in products:
            sku = product.get("sku")
            name = product.get("name")
            store = product.get("store")
            names[sku, store] = name

        inventory = ShopperMySQLInterface.list_all_inventory(userid)
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


class ShopperDataInterface:
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
    def delete_all_inventory(cls, userid):
        pass

    @classmethod
    def list_all_inventory(cls, userid):
        pass


class ShopperMySQLInterface(ShopperDataInterface):
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
