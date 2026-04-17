import functools

_decorated_tests = []

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

class SkipTest(Exception):
    pass

def get_decorated_tests():
    """Return list of functions marked with @test"""
    return _decorated_tests.copy()
