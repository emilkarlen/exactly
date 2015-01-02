__author__ = 'emil'

import unittest

from shelltest_test.phase_instr import test_suite
from shelltest_test import test_shelltest


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(test_shelltest.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
