from http import HTTPStatus
from datetime import datetime
import json
import traceback
import MySQLdb
from loguru import logger
import decimal
import re

logger.add("logs/default.log")


class MySQLHandle:
    """MySQLHandle as context management
    Always check if self.conn is None (connection error, report internal error)
    """

    def __init__(
            self,
            host="localhost",
            username="hellokitty",
            password="Hellokitty.618",
            dbname="local_shopper"
    ):
        self.host = host
        self.username = username
        self.password = password
        self.dbname = dbname
        self.conn = None

    def __enter__(self):
        try:
            self.conn = MySQLdb.connect(
                host=self.host,
                user=self.username,
                passwd=self.password,
                db=self.dbname
            )
        except Exception:
            logger.exception(f"{type(self).__name__} : Connection to database failed.")
            # avoid ide warning, Exception will not be raised due to return in finally
            raise
        finally:
            return self

    def run(self, query, data, commit=False, many=False):
        """Run query as prepared statement, assuming connection is successful
        Default is read-only query, return data from fetchall().
        When commit is True, execute writable query and return True/False.
        """
        # update
        if commit:
            result = False
        # default read
        else:
            result = ()

        cur = None
        try:
            cur = self.conn.cursor()
            if commit:
                if many:
                    cur.executemany(query, data)
                else:
                    cur.execute(query, data)
                self.conn.commit()
                result = True
            else:
                cur.execute(query, data)
                result = cur.fetchall()
        except Exception:
            logger.exception(f"{type(self).__name__} : {query}")
            # avoid ide warning, Exception will not be raised due to return in finally
            raise
        finally:
            if cur:
                cur.close()
            return result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()


class AppException(Exception):
    """AppException base class for all exceptions"""

    status = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, *args, client_msg=None):
        """

        Args:
            client_msg (str, optional): message for client. Defaults to None.
        """
        if args:
            super().__init__(*args)
            self._internal_msg = args[0]
        else:
            super().__init__(self.status.phrase)
            self._internal_msg = self.status.phrase

        if client_msg is not None:
            self._client_msg = client_msg
        else:
            self._client_msg = self._internal_msg

        self._time_utc = datetime.utcnow().isoformat()

    @property
    def info(self):
        """Information to client

        Returns:
            str: serialized json object of info to user
        """
        data = {
            "code": self.status.value,
            "message": self._client_msg,
            "category": type(self).__name__,
            "time_utc": self._time_utc
        }
        return json.dumps(data)

    @property
    def traceback(self):
        """

        Returns:
            _type_: traceback generator
        """
        return traceback.TracebackException.from_exception(self).format()

    def log(self):
        """Log information for debug
        """
        ex = {
            "time_utc": self._time_utc,
            "message": self._internal_msg,
            "category": type(self).__name__,
            "args": self.args[1:],
            "traceback": list(self.traceback)
        }
        # TODO: extend
        print(ex)


class ClientException(AppException):
    """ClientException subclass for exceptions caused by client"""

    status = HTTPStatus.BAD_REQUEST


class InvalidInputException(AppException):
    """ClientException subclass for exceptions caused by invalid input"""

    status = HTTPStatus.BAD_REQUEST


class NotAuthorizedException(ClientException):
    """NotAuthorizedError subclass for exceptions caused by failed client authentication"""

    status = HTTPStatus.UNAUTHORIZED


class NotFoundException(ClientException):
    """NotFoundError subclass for exceptions caused by failed resource lookup"""

    status = HTTPStatus.NOT_FOUND


class InternalException(AppException):
    """InternalException subclass for exceptions caused by server"""

    status = HTTPStatus.INTERNAL_SERVER_ERROR


class APIException(AppException):
    """APIException subclass for exceptions caused by API errors"""

    status = HTTPStatus.NOT_IMPLEMENTED


class DBException(InternalException):
    """APIException subclass for exceptions caused by database errors"""

    status = HTTPStatus.SERVICE_UNAVAILABLE


class UIException(InternalException):
    """APIException subclass for exceptions caused by UI errors"""

    status = HTTPStatus.GATEWAY_TIMEOUT


class ValueConverter:
    """Base class to convert value to desired type
    It can be initialized with given value, attribute `value` is converted
    value, if valid.
    It can also be initialized without given value, calling `convert(value)` set
    attribute `value` with converted value and return converted value, if valid.
    """

    def __init__(self, value=None):
        """

        Args:
            value (type, optional): input value. Defaults to None.
        """
        self.value = value

    @property
    def value(self):
        """

        Returns:
            type: converted value
        """
        return self._value

    def convert(self, value):
        """Convert value to desired type and return, implemented in subclasses

        Args:
            value (type): input value
        """
        pass

    @value.setter
    def value(self, value):
        """

        Args:
            value (type): input value
        """
        if value is None:
            self._value = None
        else:
            self.convert(value)


# noinspection PyBroadException
class IntConverter(ValueConverter):
    """Sub class to convert value to integer

    Convert non-boolean value to Decimal object and check if Decimal == int(Decimal).
    If include_bool_str is True, also check if value is boolean value or any of "t",
    "true", "f", "false" or related.
    """

    def __init__(self, value=None, include_bool_str=False):
        """

        Args:
            value (type): input value
            include_bool_str (bool, optional): convert boolean to integer. Defaults to False.
        """
        self._include_bool_str = include_bool_str
        super().__init__(value)

    @property
    def value(self):
        """

        Returns:
            type: converted value
        """
        return self._value

    @logger.catch
    def convert(self, value, include_bool_str=False):
        """Convert non-boolean value to Decimal object and check if Decimal == int(Decimal).
        If include_bool_str is True, also check if value is boolean value or any of "t",
        "true", "f", "false" or related.

        Args:
            value (type): input value
            include_bool_str (bool, optional): convert boolean to integer. Defaults to False.

        Returns:
            int/NoneType: converted value
        """
        self._include_bool_str = include_bool_str
        self._value = None
        if value is None:
            return None

        if self._include_bool_str:
            if isinstance(value, str):
                temp = value.strip().casefold()
                if temp in ("t", "true"):
                    self._value = 1
                    return self._value
                if temp in ("f", "false"):
                    self._value = 0
                    return self._value
        try:
            if not self._include_bool_str and isinstance(value, bool):
                raise TypeError
            d = decimal.Decimal(value)
            if d == int(d):
                self._value = int(d)
        except (TypeError, decimal.InvalidOperation):
            logger.debug(f"{type(self).__name__} : {value}")
        except:
            logger.exception(f"{type(self).__name__} : {value}")
        finally:
            return self._value

    @value.setter
    def value(self, value):
        """

        Args:
            value (type): input value
        """
        if value is None:
            self._value = None
        else:
            self.convert(value, self._include_bool_str)


class StrAlnumConverter(ValueConverter):
    """Sub class to convert value to string with only alphabetical
    characters and numbers

    Strip and replace all special characters with "".
    """
    def convert(self, value):
        """Strip and replace all special characters with "".

        Args:
            value (type): input value

        Returns:
            str/NoneType: converted value
        """
        self._value = None
        if value is not None:
            if isinstance(value, str):
                self._value = re.sub("[^A-Za-z0-9]+", "", value.strip())
        return self._value


class StrAlnumSpaceConverter(ValueConverter):
    """Sub class to convert value to string with only alphabetical
    characters, numbers and space

    Strip and replace all special characters except space with "".
    """
    def convert(self, value):
        """Strip and replace all special characters except space with "".

        Args:
            value (type): input value

        Returns:
            str/NoneType: converted value
        """
        self._value = None
        if value is not None:
            if isinstance(value, str):
                self._value = re.sub("[^A-Za-z0-9 ]+", "", value.strip())
        return self._value
