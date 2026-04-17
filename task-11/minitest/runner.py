import time
import inspect
from .discovery import discover_tests
from .result import TestResult, TestCase
from .parallel import run_parallel
from .decorators import SkipTest
from .fixtures import _fixtures, _fixture_cleanup, run_teardowns, FixtureScope, get_fixture_value

class Runner:
    def __init__(self, directory, parallel=1, verbose=False):
        self.directory = directory
        self.parallel = parallel
        self.verbose = verbose
        self.session_fixtures_run = False
    
    def run(self):
        tests = discover_tests(self.directory)
        
        if not tests:
            print("No tests found")
            return TestResult()
        
        if not self.session_fixtures_run:
            self._setup_session_fixtures()
            self.session_fixtures_run = True
        
        module_paths = {}
        for test in tests:
            module_paths[test.module] = test.module
        
        if self.parallel > 1:
            results_data = run_parallel(tests, module_paths, self.parallel)
            result = self._process_parallel_results(results_data)
        else:
            result = self._run_sequential(tests)
        
        run_teardowns(FixtureScope.SESSION)
        
        return result
    
    def _setup_session_fixtures(self):
        for name, fixture_data in _fixtures.items():
            if fixture_data.get("scope") == FixtureScope.SESSION and not fixture_data.get("is_setup"):
                value = fixture_data["func"]()
                fixture_data["value"] = value
                _fixture_cleanup[FixtureScope.SESSION].append(name)
    
    def _setup_module_fixtures(self, module_name):
        for name, fixture_data in _fixtures.items():
            if fixture_data.get("scope") == FixtureScope.MODULE and not fixture_data.get("is_setup"):
                if hasattr(fixture_data["func"], "__module__") and fixture_data["func"].__module__ == module_name:
                    value = fixture_data["func"]()
                    fixture_data["value"] = value
                    _fixture_cleanup[FixtureScope.MODULE].append(name)

    def _resolve_fixtures(self, func):
        """Inspect function arguments and inject matching fixtures."""
        sig = inspect.signature(func)
        kwargs = {}
        for param_name in sig.parameters:
            if param_name in _fixtures:
                # Reset function-scoped fixtures each time
                if _fixtures[param_name].get("scope") == FixtureScope.FUNCTION:
                    _fixtures[param_name]["value"] = None
                kwargs[param_name] = get_fixture_value(param_name)
        return kwargs

    def _run_one(self, test, test_case, result, extra_kwargs=None):
        """Run a single test function, injecting fixtures, return True if passed."""
        kwargs = self._resolve_fixtures(test.func)
        if extra_kwargs:
            kwargs.update(extra_kwargs)
        start = time.time()
        try:
            test.func(**kwargs)
            duration = time.time() - start
            test_case.duration = duration
            result.add_pass(test_case)
            if self.verbose:
                label = f"{test.full_name()}"
                if extra_kwargs:
                    label += f"{extra_kwargs}"
                print(f"PASS {label} [{duration:.3f}s]")
            return True
        except SkipTest as e:
            duration = time.time() - start
            test_case.duration = duration
            result.add_skip(test_case, str(e))
            if self.verbose:
                print(f"SKIP {test.full_name()} [{duration:.3f}s] {str(e)}")
        except AssertionError as e:
            duration = time.time() - start
            test_case.duration = duration
            result.add_fail(test_case, str(e))
            if self.verbose:
                label = f"{test.full_name()}"
                if extra_kwargs:
                    label += f"{extra_kwargs}"
                print(f"FAIL {label} [{duration:.3f}s]\n   {e}")
        except Exception as e:
            duration = time.time() - start
            test_case.duration = duration
            result.add_error(test_case, str(e))
            if self.verbose:
                label = f"{test.full_name()}"
                if extra_kwargs:
                    label += f"{extra_kwargs}"
                print(f"ERROR {label} [{duration:.3f}s]\n   {e}")
        return False

    def _run_sequential(self, tests):
        result = TestResult()
        current_module = None
        
        for test in tests:
            if test.module != current_module:
                run_teardowns(FixtureScope.MODULE)
                self._setup_module_fixtures(test.module)
                current_module = test.module
            
            test_case = TestCase(
                name=test.name,
                module=test.module,
                func=test.func
            )
            
            if hasattr(test.func, "__skipped__"):
                result.add_skip(test_case, test.func.__skip_reason__)
                if self.verbose:
                    print(f"SKIP {test.full_name()} [{test.func.__skip_reason__}]")
                continue
            
            if test.is_parametrized():
                for params in test.get_parameter_sets():
                    self._run_one(test, test_case, result, extra_kwargs=params)
            else:
                self._run_one(test, test_case, result)
        
        run_teardowns(FixtureScope.MODULE)
        
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
            elif status == 'skip':
                result.add_skip(test_case, error_msg)
                if self.verbose:
                    print(f"SKIP {full_name} [{duration:.3f}s] {error_msg}")
            elif status == 'error':
                result.add_error(test_case, error_msg)
                if self.verbose:
                    print(f"ERROR {full_name} [{duration:.3f}s]\n   {error_msg}")
        
        return result
