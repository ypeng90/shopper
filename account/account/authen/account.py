"""A Simple Account Management Module"""

from django.conf import settings
from django.utils import timezone
from authen.data import AuthenMySQLInterface
from datetime import datetime, timedelta
from hashlib import sha256
import importlib.util
import jwt
from loguru import logger
import os

logger.add("logs/default.log")

spec = importlib.util.spec_from_file_location("utils",
                                              os.path.join(settings.BASE_DIR,
                                                           "account/utils.py"))
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)


class Register:
    def __init__(self, name, passwd):
        self._name = name
        self._userid = self._generate_userid()
        # Must before generating password.
        self._salt = self._generate_salt()
        self._password = self._hash_password(passwd)

    @staticmethod
    def _generate_userid():
        curr = sha256(bytes(
            datetime.utcnow().isoformat() + settings.SECRET_KEY,
            "utf-8"
        )).digest()
        while True:
            worker = sha256(curr)
            curr = worker.digest()
            value = worker.hexdigest()
            if value[:8].isdigit() and value[0] != "0":
                userid = int(value[:8])
                # TODO: check if userid is already existing
                return userid

    @staticmethod
    def _generate_salt():
        hashed = sha256(bytes(
            datetime.utcnow().isoformat() + settings.SECRET_KEY,
            "utf-8"
        )).hexdigest()
        return hashed

    def _hash_password(self, passwd):
        for _ in range(1000):
            passwd = sha256(bytes(
                self._salt + passwd + settings.SECRET_KEY,
                "utf-8"
            )).hexdigest()
        return passwd

    @property
    def existing(self):
        return bool(AuthenMySQLInterface.retrieve_id_by_name(self._name))

    def add(self):
        """Add to db when username not existing"""

        return AuthenMySQLInterface.add_new_account(
            self._name,
            self._userid,
            self._password,
            self._salt,
            True
        )


class Login:
    def __init__(self, name, passwd):
        self._name = name
        self._userid = None
        self._salt = None
        self._password = passwd

    def _get_account(self):
        result = AuthenMySQLInterface.retrieve_id_salt_by_name(self._name)
        if bool(result):
            self._userid, self._salt = result[0]

    def _hash_password(self):
        for _ in range(1000):
            self._password = sha256(bytes(
                self._salt + self._password + settings.SECRET_KEY,
                "utf-8"
            )).hexdigest()
        return self._password

    @property
    def existing(self):
        self._get_account()
        if self._userid is None:
            return False

        return bool(AuthenMySQLInterface.retrieve_id_by_name_passwd(
            self._name,
            self._hash_password()
        ))

    def jwt(self):
        payload = {
            "exp": timezone.now() + timedelta(days=1),
            "userid": self._userid,
            "authenticated": True
        }
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        return token
