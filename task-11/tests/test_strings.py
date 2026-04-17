from minitest.decorators import skip, test
from minitest.assertions import assert_equal

def test_upper():
    result = "hello".upper()
    assert result == "HELLO"

def test_lower():
    result = "WORLD".lower()
    assert result == "world"

def test_contains():
    assert "cat" in "concatenate"

@skip("regex not implemented yet")
def test_regex():
    assert "123".isdigit()

@test
def custom_named_test():
    assert "hello".capitalize() == "Hello"

def test_assertion_diff_demo():
    expected = "Hello World"
    actual = "Hello Python"
    assert_equal(actual, expected)
