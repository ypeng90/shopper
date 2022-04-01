"""
Tests for Converter classes
Command line: python -m pytest ./test_valueconverter.py
"""

import pytest
from utils import IntConverter, StrAlnumConverter


@pytest.mark.parametrize(
    "input_val, output_val",
    [
        (5, 5),
        (-5, -5),
        (5., 5),
        (-5., -5),
        (5.0, 5),
        (-5.0, -5),
        ("5", 5),
        ("-5", -5),
        ("5.", 5),
        ("-5.", -5),
        ("5.0", 5),
        ("-5.0", -5),
        (" -5", -5),
        ("-5 ", -5),
        (" -5 ", -5),
        (None, None),
        (5.5, None),
        ("5.5", None),
        (True, None),
        (bool(10), None),
        (1 == 1, None),
        (False, None),
        (bool(0), None),
        (1 == 2, None),
        ("t", None),
        ("true", None),
        ("f", None),
        ("false", None),
        (dict(), None),
    ]
)
def test_intconverter_ok(input_val, output_val):
    assert IntConverter(input_val).value == output_val


@pytest.mark.parametrize(
    "input_val, output_val",
    [
        ("t", 1),
        ("T", 1),
        ("true", 1),
        ("True", 1),
        ("TRUE", 1),
        ("f", 0),
        ("F", 0),
        ("false", 0),
        ("False", 0),
        ("FALSE", 0),
        (True, 1),
        (bool(10), 1),
        (1 == 1, 1),
        (False, 0),
        (bool(0), 0),
        (1 == 2, 0),
    ]
)
def test_intconverter_include_boolean_ok(input_val, output_val):
    assert IntConverter(input_val, include_bool_str=True).value == output_val


@pytest.mark.parametrize(
    "input_val, output_val",
    [
        (5, 5),
        (-5, -5),
        (5., 5),
        (-5., -5),
        (5.0, 5),
        (-5.0, -5),
        ("5", 5),
        ("-5", -5),
        ("5.", 5),
        ("-5.", -5),
        ("5.0", 5),
        ("-5.0", -5),
        (" -5", -5),
        ("-5 ", -5),
        (" -5 ", -5),
        (None, None),
        (5.5, None),
        ("5.5", None),
        (True, None),
        (bool(10), None),
        (1 == 1, None),
        (False, None),
        (bool(0), None),
        (1 == 2, None),
        ("t", None),
        ("true", None),
        ("f", None),
        ("false", None),
        (dict(), None),
    ]
)
def test_intconverter_convert_ok(input_val, output_val):
    handle = IntConverter()
    result = handle.convert(input_val)
    assert result == output_val


@pytest.mark.parametrize(
    "input_val, output_val",
    [
        ("t", 1),
        ("T", 1),
        ("true", 1),
        ("True", 1),
        ("TRUE", 1),
        ("f", 0),
        ("F", 0),
        ("false", 0),
        ("False", 0),
        ("FALSE", 0),
        (True, 1),
        (bool(10), 1),
        (1 == 1, 1),
        (False, 0),
        (bool(0), 0),
        (1 == 2, 0),
    ]
)
def test_intconverter_convert_include_boolean_ok(input_val, output_val):
    handle = IntConverter()
    result = handle.convert(input_val, include_bool_str=True)
    assert result == output_val


@pytest.mark.parametrize(
    "input_val, output_val",
    [
        ("a", "a"),
        (" a", "a"),
        ("a ", "a"),
        (" a ", "a"),
        ("a;", "a"),
        ("a\;", "a"),
        ("&a|", "a"),
        (None, None),
        ([], None),
    ]
)
def test_stralnumconverter_ok(input_val, output_val):
    assert StrAlnumConverter(input_val).value == output_val


@pytest.mark.parametrize(
    "input_val, output_val",
    [
        ("a", "a"),
        (" a", "a"),
        ("a ", "a"),
        (" a ", "a"),
        ("a;", "a"),
        ("a\;", "a"),
        ("&a|", "a"),
        (None, None),
        ([], None),
    ]
)
def test_stralnumconverter_convert_ok(input_val, output_val):
    handle = StrAlnumConverter()
    result = handle.convert(input_val)
    assert result == output_val
