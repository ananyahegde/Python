import functools

_decorated_tests = []

class SkipTest(Exception):
    pass


def test(func):
    """Decorator to mark a function as a test"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    _decorated_tests.append(func)
    return wrapper

def skip(reason="skipped"):
    """Decorator to skip a test"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            raise SkipTest(reason)
        wrapper.__skip_reason__ = reason
        wrapper.__skipped__ = True
        return wrapper
    return decorator

def parametrize(argnames, argvalues):
    """Decorator to run a test with multiple input sets"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        keys = [k.strip() for k in argnames.split(",")]
        wrapper.__parametrize_keys__ = keys
        wrapper.__parametrize_values__ = argvalues
        return wrapper
    return decorator

def get_decorated_tests():
    """Return list of functions marked with @test"""
    return _decorated_tests.copy()
