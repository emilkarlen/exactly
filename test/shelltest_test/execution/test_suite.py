__author__ = 'emil'

import unittest

from shelltest_test import execution


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(execution.test_execution_directory_structure.suite())
    ret_val.addTest(execution.test_execution.suite())
    ret_val.addTest(execution.test_execution_sequence.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
