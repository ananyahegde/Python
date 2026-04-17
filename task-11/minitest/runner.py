import time
from .discovery import discover_tests
from .result import TestResult, TestCase
from .parallel import run_parallel

class Runner:
    def __init__(self, directory, parallel=1, verbose=False):
        self.directory = directory
        self.parallel = parallel
        self.verbose = verbose
    
    def run(self):
        tests = discover_tests(self.directory)
        
        if not tests:
            print("No tests found")
            return TestResult()
        
        module_paths = {}
        for test in tests:
            module_paths[test.module] = test.module
        
        if self.parallel > 1:
            results_data = run_parallel(tests, module_paths, self.parallel)
            result = self._process_parallel_results(results_data)
        else:
            result = self._run_sequential(tests)
        
        return result
    
    def _run_sequential(self, tests):
        result = TestResult()
        
        for test in tests:
            test_case = TestCase(
                name=test.name,
                module=test.module,
                func=test.func
            )
            
            start = time.time()
            try:
                test.func()
                duration = time.time() - start
                test_case.duration = duration
                result.add_pass(test_case)
                if self.verbose:
                    print(f"PASS {test.full_name()} [{duration:.3f}s]")
            except AssertionError as e:
                duration = time.time() - start
                test_case.duration = duration
                result.add_fail(test_case, str(e))
                if self.verbose:
                    print(f"FAIL {test.full_name()} [{duration:.3f}s]\n   {e}")
            except Exception as e:
                duration = time.time() - start
                test_case.duration = duration
                result.add_error(test_case, str(e))
                if self.verbose:
                    print(f"ERROR {test.full_name()} [{duration:.3f}s]\n   {e}")
        
        return result
    
    def _process_parallel_results(self, results_data):
        result = TestResult()
        
        for status, full_name, duration, error_msg in results_data:
            parts = full_name.rsplit('.', 1)
            module = parts[0] if len(parts) > 1 else ""
            name = parts[-1]
            
            test_case = TestCase(
                name=name,
                module=module,
                func=None,
                duration=duration
            )
            
            if status == 'pass':
                result.add_pass(test_case)
                if self.verbose:
                    print(f"PASS {full_name} [{duration:.3f}s]")
            elif status == 'fail':
                result.add_fail(test_case, error_msg)
                if self.verbose:
                    print(f"FAIL {full_name} [{duration:.3f}s]\n   {error_msg}")
            elif status == 'error':
                result.add_error(test_case, error_msg)
                if self.verbose:
                    print(f"ERROR {full_name} [{duration:.3f}s]\n   {error_msg}")
        
        return result
