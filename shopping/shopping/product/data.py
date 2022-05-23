"""Data Module"""

from product.utils import MySQLHandle
from loguru import logger

logger.add("logs/default.log")


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
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT zipcode FROM product_zipcodes WHERE userid = %s"
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def update_zipcode(cls, userid, zipcode):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT INTO product_zipcodes (userid, zipcode) "
                    "VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE zipcode=VALUES(zipcode)"
                )
                result = db.run(query, (userid, zipcode), commit=True)
            else:
                result = None
        return result

    @classmethod
    def list_all_products(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = """
                SELECT json_arrayagg(
                    json_object(
                        'sku', sku,
                        'name', name,
                        'store', store,
                        'track', track
                    )
                )
                FROM product_products
                WHERE userid = %s
                """
                # 51589605
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def list_all_track_products(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = """
                SELECT json_arrayagg(
                    json_object(
                        'sku', sku,
                        'store', store
                    )
                )
                FROM product_products
                WHERE userid = %s AND track = 1
                """
                # 51589605
                result = db.run(query, (userid,))
            else:
                result = None
        return result

    @classmethod
    def update_product(cls, userid, sku, store, track):
        with MySQLHandle() as db:
            if db.conn:
                query = "UPDATE product_products SET track = %s WHERE userid = %s AND sku = %s AND store = %s"
                result = db.run(query, (track, userid, sku, store), commit=True)
            else:
                result = None
        return result

    @classmethod
    def add_product(cls, userid, sku, name, store):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO product_products (userid, sku, name, store, track) "
                    "VALUES (%s, %s, %s, %s, 1)"
                )
                result = db.run(query, (userid, sku, name, store), commit=True)
            else:
                result = None
        return result

    @classmethod
    def delete_all_inventory(cls, userid):
        with MySQLHandle() as db:
            if db.conn:
                query = "DELETE FROM product_inventory WHERE userid = %s"
                result = db.run(query, (userid,), commit=True)
            else:
                result = None
        return result

    @classmethod
    def get_mapping_by_zipcode_store(cls, store, zipcode):
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT * FROM product_zipcodestoresmapping WHERE store = %s AND zipcode = %s"
                result = db.run(query, (store, zipcode))
            else:
                result = None
        return result

    @classmethod
    def add_stores(cls, data):
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO product_stores "
                    "(store, store_id, store_name, address, city, state, zipcode, location) "
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
                    "INSERT IGNORE INTO product_zipcodestoresmapping (store, zipcode, store_id) "
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
                        FROM product_inventory
                        WHERE sku = %s AND store = %s AND check_time > DATE_SUB(NOW(6), INTERVAL 1 HOUR)
                    ) got
                    INNER JOIN
                    (
                        SELECT store_id
                        FROM product_zipcodestoresmapping
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
                query = "SELECT * FROM product_stores WHERE store = %s AND zipcode = %s LIMIT 1"
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
                    "INSERT INTO product_inventory (sku, quantity, store, store_id, check_time) "
                    "VALUES (%s, %s, %s, %s, NOW(6)) "
                    "ON DUPLICATE KEY UPDATE quantity=VALUES(quantity), check_time=NOW(6)"
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
                            FROM product_inventory
                        ) q
                        INNER JOIN
                        (
                            SELECT sku, name, store
                            FROM product_products
                            WHERE userid = %s AND track = 1
                        ) p
                        ON q.sku = p.sku AND q.store = p.store
                        INNER JOIN
                        (
                            SELECT store, store_id
                            FROM product_zipcodestoresmapping
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
                        FROM product_stores
                    ) s
                    ON p.store = s.store AND p.store_id = s.store_id
                """
                # 51589605, 92128
                result = db.run(query, (userid, zipcode))
            else:
                result = None
        return result
