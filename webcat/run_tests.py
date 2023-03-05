# run all unittests in tests folder

import unittest
import os

def run_tests():
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__)) + "/tests"
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    run_tests()
