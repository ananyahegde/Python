from multiprocessing import Pool
import time
import importlib
import sys

def run_test_worker(args):
    test_info, module_path = args

    try:
        if module_path not in sys.modules:
            importlib.import_module(module_path)

        module = sys.modules[module_path]
        test_func = getattr(module, test_info.name)

        start = time.time()
        test_func()
        duration = time.time() - start

        return ('pass', test_info.full_name(), duration, None)

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
