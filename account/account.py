"""A Simple Account Management Module"""

from django.conf import settings
from django.utils import timezone
from account.utils import MySQLHandle
from datetime import datetime, timedelta
from hashlib import sha256
import jwt
from loguru import logger
import random

logger.add("logs/default.log")

# Create directly in MySQL
# CREATE TABLE users
# (
#     userid int NOT NULL,
#     username varchar(20) NOT NULL UNIQUE,
#     password char(64) NOT NULL,
#     salt char(4) NOT NULL,
#     reg_date datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     PRIMARY KEY (userid)
# );


class Register:
    def __init__(self, name, passwd):
        self.userid = self._generate_userid()
        self.name = name
        self.salt = self._generate_salt()
        self.password = self._hash_password(passwd)

    @staticmethod
    def _generate_userid():
        curr = sha256(bytes(datetime.utcnow().isoformat(), "utf-8")).digest()
        while True:
            worker = sha256(curr)
            curr = worker.digest()
            value = worker.hexdigest()
            if value[:8].isdigit() and value[0] != "0":
                return int(value[:8])

    @staticmethod
    def _generate_salt():
        hashed = sha256(bytes(datetime.utcnow().isoformat(), "utf-8")).hexdigest()
        random.seed(datetime.utcnow())
        salt = []
        for _ in range(4):
            salt.append(hashed[random.randint(0, 63)])
        return "".join(salt)

    def _hash_password(self, passwd):
        return sha256(bytes(self.salt + passwd, "utf-8")).hexdigest()

    @property
    def existing(self):
        return bool(AccountMySQLInterface.retrieve_id_by_name(self.name))

    def add(self):
        """Add to db when username not existing"""

        return AccountMySQLInterface.add_new_account(self.userid, self.name, self.password, self.salt, True)


class Login:
    def __init__(self, name, passwd):
        self.userid = None
        self.name = name
        self.password = passwd
        self.salt = None

    def _get_account(self):
        result = AccountMySQLInterface.retrieve_id_salt_by_name(self.name)
        if bool(result):
            self.userid, self.salt = result[0]

    def _hash_password(self):
        return sha256(bytes(self.salt + self.password, "utf-8")).hexdigest()

    @property
    def existing(self):
        self._get_account()
        if self.userid is None:
            return False

        return bool(AccountMySQLInterface.retrieve_id_by_name_passwd(self.name, self._hash_password()))

    def jwt(self):
        payload = {
            "exp": timezone.now() + timedelta(days=1),
            "userid": self.userid
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token


class AccountDataInterface:
    @classmethod
    def add_new_account(cls, userid, name, password, salt, commit):
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


class AccountMySQLInterface(AccountDataInterface):
    """Data interface for Account implemented with MySQL"""

    @classmethod
    def add_new_account(cls, userid, name, password, salt, commit):
        result = False
        with MySQLHandle() as db:
            if db.conn:
                query = (
                    "INSERT IGNORE INTO users (userid, username, password, salt)"
                    "VALUES (%s, %s, %s, %s)"
                )
                result = db.run(query, (userid, name, password, salt), commit=commit)
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_id_by_name(cls, name):
        result = ()
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT userid FROM users WHERE username = %s"
                result = db.run(query, (name,))
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_id_salt_by_name(cls, name):
        result = ()
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT userid, salt FROM users WHERE username = %s"
                result = db.run(query, (name,))
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_id_by_name_passwd(cls, name, passwd):
        result = ()
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT userid FROM users WHERE username = %s AND password = %s"
                result = db.run(query, (name, passwd))
            else:
                print("Server Error")
        return result

    @classmethod
    def retrieve_name_by_id(cls, userid):
        result = ()
        with MySQLHandle() as db:
            if db.conn:
                query = "SELECT username FROM users WHERE userid = %s"
                result = db.run(query, (userid,))
            else:
                print("Server Error")
        return result
