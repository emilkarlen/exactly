import unittest

from shellcheck_lib_test import test_suite


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_suite.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
