import pytest


from estimap_recreation.panos import add_one
from estimap_recreation.panos import add_two
from estimap_recreation.panos import add_ten


def test_add_one():
    assert add_one(0) == 1
    assert add_one(1) == 2
    assert add_one(10) == 11


def test_add_two():
    assert add_one(0) == 2
    assert add_one(1) == 3
    assert add_one(10) == 12


def test_add_ten():
    assert add_ten(0) == 10
    assert add_ten(1) == 11
    assert add_ten(10) == 20
