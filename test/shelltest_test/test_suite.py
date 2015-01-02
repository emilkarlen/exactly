__author__ = 'emil'

import unittest

from shelltest_test import test_shelltest
from shelltest_test import test_sect_instr
from shelltest_test import test_parse
from shelltest_test import test_line_source
from shelltest_test import test_syntax


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_shelltest.suite())
    ret_val.addTest(test_sect_instr.suite())
    ret_val.addTest(test_parse.suite())
    ret_val.addTest(test_line_source.suite())
    ret_val.addTest(test_syntax.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
