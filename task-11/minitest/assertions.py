import difflib

def assert_equal(actual, expected, context=""):
    if actual != expected:
        diff = _make_diff(actual, expected)
        raise AssertionError(f"{context}\nExpected: {expected}\nActual:   {actual}\n{diff}" if context else f"Expected: {expected}\nActual:   {actual}\n{diff}")

def assert_true(value, context=""):
    if not value:
        raise AssertionError(f"{context}\nExpected True, got {value}" if context else f"Expected True, got {value}")

def assert_false(value, context=""):
    if value:
        raise AssertionError(f"{context}\nExpected False, got {value}" if context else f"Expected False, got {value}")

def assert_in(item, container, context=""):
    if item not in container:
        raise AssertionError(f"{context}\n{item} not found in {container}" if context else f"{item} not found in {container}")

def _make_diff(actual, expected):
    if isinstance(actual, str) and isinstance(expected, str):
        diff = difflib.unified_diff(
            expected.splitlines(),
            actual.splitlines(),
            fromfile='expected',
            tofile='actual',
            lineterm=''
        )
        return '\n' + '\n'.join(diff)
    
    return f"\n  Expected: {repr(expected)}\n  Actual:   {repr(actual)}"
