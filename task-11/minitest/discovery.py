import os
import importlib
import inspect
from typing import List, Dict, Callable, Any

class TestInfo:
    """Holds information about a single test"""
    def __init__(self, name: str, module: str, func: Callable, file_path: str):
        self.name = name
        self.module = module
        self.func = func
        self.file_path = file_path
    
    def full_name(self) -> str:
        return f"{self.module}.{self.name}"

def discover_tests(directory: str) -> List[TestInfo]:
    """
    Find all tests in a directory.
    Looks for either unctions named test_* or functions decorated with @test
    """

    tests = []

    # Walk through all files in directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.startswith('test_') or not file.enswith('.py'):
                continue

            # Convert file path to Python moule path
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, start=os.getcwd())
            module_path = rel_path.replace('/', '.').replace('\\', '.')[:-3]

            try:
                module = importlib.import_module(module_path)
            except Exception as e:
                print(f"Warning: Could not import {module_path}: {e}")
                continue

            # Find all test functions
            for name, obj in inspect.getmembers(module):
                if name.startswith('test_') and inspect.isfunction(obj):
                    tests.append(TestInfo(
                        name=name,
                        module=module_path,
                        func=obj,
                        file_path=file_path
                    ))

    return tests
