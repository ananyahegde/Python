import os
import importlib
import inspect
from typing import List
from .decorators import get_decorated_tests

class TestInfo:
    def __init__(self, name: str, module: str, func: callable, file_path: str):
        self.name = name
        self.module = module
        self.func = func
        self.file_path = file_path
    
    def full_name(self) -> str:
        return f"{self.module}.{self.name}"

def discover_tests(directory: str) -> List[TestInfo]:
    tests = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, start=os.getcwd())
            module_path = rel_path.replace('/', '.').replace('\\', '.')[:-3]
            
            try:
                module = importlib.import_module(module_path)
            except Exception:
                continue
            
            for name, obj in inspect.getmembers(module):
                is_named_test = name.startswith('test_') and inspect.isfunction(obj)
                is_decorated_test = obj in get_decorated_tests()
                
                if (is_named_test or is_decorated_test) and inspect.isfunction(obj):
                    tests.append(TestInfo(
                        name=name,
                        module=module_path,
                        func=obj,
                        file_path=file_path
                    ))
    
    return tests
