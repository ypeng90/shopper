"""Data Module"""

from django.conf import settings
import importlib.util
from loguru import logger
import os


logger.add("logs/default.log")

spec = importlib.util.spec_from_file_location("utils",
                                              os.path.join(settings.BASE_DIR,
                                                           "shopper/utils.py"))
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

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
# MySQL uses POINT(lat, long)
# GeoJSON uses "coordinates": [long, lat]
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


class ProductDataInterface:
    """Data interface for Scraper base class"""

    @classmethod
    def get_zipcode(cls, userid):
        pass

    @classmethod
    def update_zipcode(cls, userid, zipcode):
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
    def get_zipcode(cls, userid):
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT zipcode FROM users WHERE userid = %s"
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def update_zipcode(cls, userid, zipcode):
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "UPDATE users SET zipcode = %s WHERE userid = %s"
                result = db.run(query, (zipcode, userid), commit=True)
            else:
                result = None
        return result

    @classmethod
    def list_all_products(cls, userid):
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT sku, name, store, track FROM products WHERE userid = %s"
                query = """
                SELECT json_arrayagg(
                    json_object(
                        'sku', sku,
                        'name', name,
                        'store', store,
                        'track', track
                    )
                )
                FROM products
                WHERE userid = %s
                """
                # 51589605
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def list_all_track_products(cls, userid):
        with utils.MySQLHandle() as db:
            if db.conn:
                query = """
                SELECT json_arrayagg(
                    json_object(
                        'sku', sku,
                        'store', store
                    )
                )
                FROM products
                WHERE userid = %s AND track = 1
                """
                # 51589605
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def update_product(cls, userid, sku, store, track):
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "UPDATE products SET track = %s WHERE userid = %s AND sku = %s AND store = %s"
                result = db.run(query, (track, userid, sku, store), commit=True)
            else:
                result = None
        return result

    @classmethod
    def add_product(cls, userid, sku, name, store):
        with utils.MySQLHandle() as db:
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
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "DELETE FROM inventory WHERE userid = %s"
                result = db.run(query, (userid,), commit=True)
            else:
                result = None
        return result

    @classmethod
    def get_mapping_by_zipcode_store(cls, store, zipcode):
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT * FROM zipcode_stores_mapping WHERE store = %s AND zipcode = %s"
                result = db.run(query, (store, zipcode))
            else:
                result = None
        return result

    @classmethod
    def add_stores(cls, data):
        with utils.MySQLHandle() as db:
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
        with utils.MySQLHandle() as db:
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
        with utils.MySQLHandle() as db:
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
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT * FROM stores WHERE store = %s AND zipcode = %s LIMIT 1"
                result = db.run(query, (store, zipcode))
            else:
                result = None
        return result

    @classmethod
    def add_quantity(cls, data):
        with utils.MySQLHandle() as db:
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
        with utils.MySQLHandle() as db:
            if db.conn:
                query = """
                    SELECT json_arrayagg(
                        json_object(
                            'type', 'Feature',
                            'geometry', s.location,
                            'properties', json_object(
                                'store', p.store,
                                'name', s.store_name,
                                'address', s.address,
                                'total', p.total,
                                'products', p.products
                            )
                        )
                    )
                    FROM
                    (
                        SELECT json_arrayagg(
                            json_object(
                                'sku', q.sku,
                                'name', p.name,
                                'quantity', q.quantity
                            )
                        ) AS products, sum(q.quantity) AS total, q.store AS store, q.store_id AS store_id
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
                            CONCAT(address, ', ', city, ', ', state, ' ', zipcode) AS address,
                            ST_AsGeoJSON(location) AS location
                        FROM stores
                    ) s
                    ON p.store = s.store AND p.store_id = s.store_id
                """
                # 51589605, 92128
                result = db.run(query, (userid, zipcode))
            else:
                result = None
        return result
