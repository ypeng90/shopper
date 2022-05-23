import decimal
from loguru import logger
import re

logger.add("logs/default.log")


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
