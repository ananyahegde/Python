from functools import wraps
from typing import Dict, Any, Callable

class FixtureScope:
    SESSION = "session"
    MODULE = "module"
    FUNCTION = "function"

_fixtures: Dict[str, Any] = {}
_fixture_cleanup: Dict[str, list] = {
    FixtureScope.SESSION: [],
    FixtureScope.MODULE: [],
    FixtureScope.FUNCTION: []
}

def fixture(scope=FixtureScope.FUNCTION):
    def decorator(func):
        _fixtures[func.__name__] = {
            "func": func,
            "scope": scope,
            "value": None
        }
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _get_or_create_fixture(func.__name__)
        
        return wrapper
    return decorator

def _get_or_create_fixture(name):
    fixture_data = _fixtures[name]
    
    if fixture_data["value"] is None:
        fixture_data["value"] = fixture_data["func"]()
        
        if fixture_data["scope"] != FixtureScope.FUNCTION:
            _fixture_cleanup[fixture_data["scope"]].append(name)
    
    return fixture_data["value"]

def setup_function(func):
    _fixtures[f"__setup__{func.__name__}"] = {
        "func": func,
        "scope": FixtureScope.FUNCTION,
        "value": None,
        "is_setup": True
    }
    return func

def teardown_function(func):
    _fixtures[f"__teardown__{func.__name__}"] = {
        "func": func,
        "scope": FixtureScope.FUNCTION,
        "value": None,
        "is_teardown": True
    }
    return func

def run_teardowns(scope):
    for name in _fixture_cleanup.get(scope, []):
        fixture_data = _fixtures.get(name)
        if fixture_data and fixture_data["value"] is not None:
            if hasattr(fixture_data["value"], "close"):
                fixture_data["value"].close()
            elif callable(getattr(fixture_data["value"], "teardown", None)):
                fixture_data["value"].teardown()
    _fixture_cleanup[scope].clear()

def get_fixture_value(name):
    return _get_or_create_fixture(name)
