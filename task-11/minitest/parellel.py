from multiprocessing import Pool
import time
import importlib
import sys
from .decorators import SkipTest

def run_test_worker(args):
    test_info, module_path = args
    
    try:
        if module_path not in sys.modules:
            importlib.import_module(module_path)
        
        module = sys.modules[module_path]
        test_func = getattr(module, test_info.name)
        
        if hasattr(test_func, "__skipped__"):
            return ('skip', test_info.full_name(), 0.0, test_func.__skip_reason__)
        
        start = time.time()
        
        if test_info.is_parametrized():
            test_func(**test_info.parametrized_cases)
        else:
            test_func()
        
        duration = time.time() - start
        return ('pass', test_info.full_name(), duration, None)
    
    except SkipTest as e:
        duration = time.time() - start
        return ('skip', test_info.full_name(), duration, str(e))
    except AssertionError as e:
        duration = time.time() - start
        return ('fail', test_info.full_name(), duration, str(e))
    except Exception as e:
        duration = time.time() - start
        return ('error', test_info.full_name(), duration, f"{type(e).__name__}: {e}")

def run_parallel(tests, module_paths, workers=4):
    args = [(test, module_paths[test.module]) for test in tests]
    
    with Pool(processes=workers) as pool:
        results = pool.map(run_test_worker, args)
    
    return results
