"""A Simple Account Management Module"""

from django.conf import settings
import importlib.util
from loguru import logger
import os

logger.add("logs/default.log")

spec = importlib.util.spec_from_file_location("utils",
                                              os.path.join(settings.BASE_DIR,
                                                           "account/utils.py"))
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

# Create directly in MySQL
# CREATE TABLE users
# (
#     userid int NOT NULL,
#     username varchar(20) NOT NULL UNIQUE,
#     password char(64) NOT NULL,
#     salt char(4) NOT NULL,
#     reg_date datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     zipcode char(5) NOT NULL DEFAULT '00000',
#     PRIMARY KEY (userid)
# );


class AuthenDataInterface:
    @classmethod
    def add_new_account(cls, name, userid, password, salt, commit):
        pass

    @classmethod
    def retrieve_id_by_name(cls, name):
        pass

    @classmethod
    def retrieve_id_salt_by_name(cls, name):
        pass

    @classmethod
    def retrieve_id_by_name_passwd(cls, name, passwd):
        pass

    @classmethod
    def retrieve_name_by_id(cls, userid):
        pass


class AuthenMySQLInterface(AuthenDataInterface):
    """Data interface for Account implemented with MySQL"""

    @classmethod
    def add_new_account(cls, name, userid, password, salt, commit):
        result = False
        with utils.MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO authen_users (username, userid, password, salt)"
                    "VALUES (%s, %s, %s, %s)"
                )
                result = db.run(query, (name, userid, password, salt), commit=commit)
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_id_by_name(cls, name):
        result = ()
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT userid FROM authen_users WHERE username = %s"
                result = db.run(query, (name,))
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_id_salt_by_name(cls, name):
        result = ()
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT userid, salt FROM authen_users WHERE username = %s"
                result = db.run(query, (name,))
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_id_by_name_passwd(cls, name, passwd):
        result = ()
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT userid FROM authen_users WHERE username = %s AND password = %s"
                result = db.run(query, (name, passwd))
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_name_by_id(cls, userid):
        result = ()
        with utils.MySQLHandle() as db:
            if db.conn:
                query = "SELECT username FROM authen_users WHERE userid = %s"
                result = db.run(query, (userid,))
            else:
                print("Server Error")
        return result
