__author__ = 'emil'

import unittest

from shelltest_test import test_shelltest


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_shelltest.suite())
    return ret_val

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
