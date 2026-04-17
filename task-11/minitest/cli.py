import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minitest.runner import Runner

def main():
    parser = argparse.ArgumentParser(description='Minitest - Simple test framework')
    parser.add_argument('command', choices=['run'])
    parser.add_argument('path', help='Directory or module to test')
    parser.add_argument('--parallel', '-p', type=int, default=1, help='Number of parallel workers')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        runner = Runner(directory=args.path, parallel=args.parallel, verbose=args.verbose)
        result = runner.run()
        
        print(f"\n=== Summary ===")
        print(f"Total: {result.total}")
        print(f"Passed: {result.passed_count}")
        print(f"Failed: {result.failed_count}")
        print(f"Skipped: {result.skipped_count}")
        print(f"Errors: {result.errors_count}")
        
        sys.exit(1 if result.failed_count > 0 or result.errors_count > 0 else 0)

if __name__ == '__main__':
    main()
