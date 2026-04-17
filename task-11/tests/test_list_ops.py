from minitest.decorators import test

def test_append():
    items = [1, 2, 3]
    items.append(4)
    assert items == [1, 2, 3, 4]

def test_pop():
    items = [1, 2, 3]
    popped = items.pop()
    assert popped == 3
    assert items == [1, 2]

def test_length_empty():
    assert len([]) == 0

def test_length_one():
    assert len([1]) == 1

def test_length_three():
    assert len([1, 2, 3]) == 3

@test
def max_value():
    assert max([1, 5, 3, 9, 2]) == 9
