__author__ = 'emil'

import unittest

import shelltest_test.test_shelltest
import shelltest_test.test_parse
import shelltest_test.test_line_source


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(shelltest_test.test_shelltest.suite())
    ret_val.addTest(shelltest_test.test_parse.suite())
    ret_val.addTest(shelltest_test.test_line_source.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
