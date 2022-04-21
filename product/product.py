"""Product Module"""

from product.scraper import ScraperTarget
from product.utils import StrAlnumSpaceConverter, MySQLHandle
import json
from loguru import logger
from time import sleep


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
#     sku varchar(15) NOT NULL,
#     quantity int NOT NULL,
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     check_time datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#     PRIMARY KEY (sku, store, store_id)
# );

# Create directly in MySQL
# CREATE TABLE zipcode_stores_mapping
# (
#     store char(3) NOT NULL,
#     zipcode char(5) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     PRIMARY KEY (store, zipcode, store_id)
# );

# Create directly in MySQL
# CREATE TABLE stores
# (
#     store char(3) NOT NULL,
#     store_id varchar(8) NOT NULL,
#     store_name varchar(48) NOT NULL,
#     address varchar(96) NOT NULL,
#     city varchar(24) NOT NULL,
#     state varchar(24) NOT NULL,
#     zipcode char(5) NOT NULL,
#     location POINT NOT NULL SRID 4326,
#     PRIMARY KEY (store, store_id)
# );


class Product:
    """Product base class"""
    
    @staticmethod
    def list_all_products(userid, track=False):
        if track:
            data = ProductMySQLInterface.list_all_track_products(userid)
        else:
            data = ProductMySQLInterface.list_all_products(userid)
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
        return ProductMySQLInterface.update_product(userid, sku, store, track)

    @staticmethod
    def search_product(store, keyword):
        if store == "tgt":
            return ScraperTarget().search_product(keyword)
        return dict()

    @staticmethod
    def add_product(userid, sku, name, store):
        name = StrAlnumSpaceConverter(name).value
        return ProductMySQLInterface.add_product(userid, sku, name, store)

    @staticmethod
    def _delete_all_inventory(userid):
        ProductMySQLInterface.delete_all_inventory(userid)

    @staticmethod
    def _get_quantity(sku, store, zipcode):
        print(f"Getting quantity for {sku} at {store} around {zipcode} ...")
        sleep(0.5)
        info = []
        if store == "tgt":
            info = ScraperTarget().get_qty_by_sku_zipcode(sku, zipcode)
        if info:
            ProductMySQLInterface.add_quantity(info)

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
        products = Product.list_all_products(userid, track=True)
        if products is None:
            return None

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
            # count of stores with latest quantity
            count = ProductMySQLInterface.count_store_with_latest(sku, store, zipcode)
            # variation exists, not always 20 matches
            if not count or count[0][0] < 18:
                Product._get_quantity(sku, store, zipcode)

        data = ProductMySQLInterface.list_all_inventory(userid, zipcode)
        if data is None:
            return None

        result = []
        for item in data:
            result.append(json.loads(item[0]))
        return result


class ProductDataInterface:
    """Data interface for Scraper base class"""

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
    def add_product(cls, userid, sku, name, store):
        pass

    @classmethod
    def delete_all_inventory(cls, userid):
        pass

    @classmethod
    def get_mapping_by_zipcode_store(cls, store, zipcode):
        pass

    @classmethod
    def add_stores(cls, data):
        pass

    @classmethod
    def add_zipcode_stores_mapping(cls, data):
        pass

    @classmethod
    def count_store_with_latest(cls, sku, store, zipcode):
        pass

    @classmethod
    def list_store_by_store_zipcode(cls, store, zipcode):
        pass

    @classmethod
    def add_quantity(cls, data):
        pass

    @classmethod
    def list_all_inventory(cls, userid, zipcode):
        pass


class ProductMySQLInterface(ProductDataInterface):
    """Data interface for Scraper implemented with MySQL"""

    @classmethod
    def list_all_products(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT sku, name, store, track FROM products WHERE userid = %s"
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def list_all_track_products(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT sku, name, store, track FROM products WHERE userid = %s AND track = 1"
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def update_product(cls, userid, sku, store, track):
        with MySQLHandle() as db:
            if db.conn:
                query = "UPDATE products SET track = %s WHERE userid = %s AND sku = %s AND store = %s"
                result = db.run(query, (track, userid, sku, store), commit=True)
            else:
                result = None
        return result

    @classmethod
    def add_product(cls, userid, sku, name, store):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO products (userid, sku, name, store) "
                    "VALUES (%s, %s, %s, %s)"
                )
                result = db.run(query, (userid, sku, name, store), commit=True)
            else:
                result = None
        return result

    @classmethod
    def delete_all_inventory(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "DELETE FROM inventory WHERE userid = %s"
                result = db.run(query, (userid,), commit=True)
            else:
                result = None
        return result

    @classmethod
    def get_mapping_by_zipcode_store(cls, store, zipcode):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT * FROM zipcode_stores_mapping WHERE store = %s AND zipcode = %s"
                result = db.run(query, (store, zipcode))
            else:
                result = None
        return result

    @classmethod
    def add_stores(cls, data):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO stores (store, store_id, store_name, address, city, state, zipcode, location) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText('POINT(%s %s)', 4326))"
                )
                result = db.run(query, data, commit=True, many=True)
            else:
                result = None
        return result

    @classmethod
    def add_zipcode_stores_mapping(cls, data):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO zipcode_stores_mapping (store, zipcode, store_id) "
                    "VALUES (%s, %s, %s)"
                )
                result = db.run(query, data, commit=True, many=True)
            else:
                result = None
        return result

    @classmethod
    def count_store_with_latest(cls, sku, store, zipcode):
        with MySQLHandle() as db:
            if db.conn:
                query = """
                    SELECT count(got.store_id)
                    FROM
                    (
                        SELECT store_id
                        FROM inventory
                        WHERE sku = %s AND store = %s AND check_time > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    ) got
                    INNER JOIN
                    (
                        SELECT store_id
                        FROM zipcode_stores_mapping
                        WHERE store = %s AND zipcode = %s 
                    ) need
                    ON got.store_id = need.store_id
                """
                result = db.run(query, (sku, store, store, zipcode))
            else:
                result = None
        return result

    @classmethod
    def list_store_by_store_zipcode(cls, store, zipcode):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT * FROM stores WHERE store = %s AND zipcode = %s LIMIT 1"
                result = db.run(query, (store, zipcode))
            else:
                result = None
        return result

    @classmethod
    def add_quantity(cls, data):
        with MySQLHandle() as db:
            if db.conn:
                # When MySQL handles `ON DUPLICATE KEY UPDATE`, it does not update `check_time` even
                # `ON UPDATE` is requested for `check_time` if new_val == old_val, i.e., no change
                # happens. Update `check_time` manually.
                query = (
                    "INSERT INTO inventory (sku, quantity, store, store_id) "
                    "VALUES (%s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE quantity=VALUES(quantity), check_time=NOW()"
                )
                result = db.run(query, data, commit=True, many=True)
            else:
                result = None
        return result
    
    @classmethod
    def list_all_inventory(cls, userid, zipcode):
        with MySQLHandle() as db:
            if db.conn:
                query = """
                    SELECT json_object(
                        'store', p.store,
                        'name', s.store_name,
                        'address', s.address,
                        'products', p.products
                    )
                    FROM
                    (
                        SELECT json_arrayagg(
                            json_object(
                                'sku', q.sku,
                                'name', p.name,
                                'quantity', q.quantity
                            )
                        ) AS products, q.store AS store, q.store_id AS store_id
                        FROM
                        (
                            SELECT sku, quantity, store, store_id
                            FROM inventory
                        ) q
                        INNER JOIN
                        (
                            SELECT sku, name, store
                            FROM products
                            WHERE userid = %s AND track = 1
                        ) p
                        ON q.sku = p.sku AND q.store = p.store
                        INNER JOIN
                        (
                            SELECT store, store_id
                            FROM zipcode_stores_mapping
                            WHERE zipcode = %s 
                        ) need
                        ON q.store = need.store AND q.store_id = need.store_id
                        GROUP BY q.store, q.store_id
                    ) p
                    INNER JOIN
                    (
                        SELECT store, store_id, store_name, 
                            CONCAT(address, ', ', city, ', ', state, ' ', zipcode) AS address
                        FROM stores
                    ) s
                    ON p.store = s.store AND p.store_id = s.store_id
                """
                result = db.run(query, (userid, zipcode))
            else:
                result = None
        return result
