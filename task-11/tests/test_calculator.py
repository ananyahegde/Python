from minitest.fixtures import fixture, FixtureScope
from minitest.decorators import skip, parametrize

@fixture(scope=FixtureScope.FUNCTION)
def calculator():
    return {"value": 0}

def test_add(calculator):
    calculator["value"] = 5 + 3
    assert calculator["value"] == 8

def test_subtract(calculator):
    calculator["value"] = 10 - 4
    assert calculator["value"] == 6

def test_multiply(calculator):
    calculator["value"] = 7 * 6
    assert calculator["value"] == 42

@skip("division not implemented")
def test_divide(calculator):
    calculator["value"] = 10 / 2
    assert calculator["value"] == 5

def test_failing():
    result = 2 * 3
    assert result == 7, f"Expected 7, got {result}"

@parametrize("a,b,expected", [
    (1, 2, 3),
    (10, 5, 15),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add_parametrized(a, b, expected):
    assert a + b == expected

@parametrize("a,b,expected", [
    (10, 3, 7),
    (5, 5, 0),
    (0, 1, -1),
])
def test_subtract_parametrized(a, b, expected):
    assert a - b == expected

@parametrize("a,b,expected", [
    (3, 4, 12),
    (7, 6, 42),
    (0, 100, 0),
])
def test_multiply_parametrized(a, b, expected):
    assert a * b == expected
