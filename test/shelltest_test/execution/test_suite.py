__author__ = 'emil'

import unittest

from shelltest_test.execution import test_execution_directory_structure
from shelltest_test.execution.test_execution_sequence import test_suite


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_execution_directory_structure.suite())
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(test_suite.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
