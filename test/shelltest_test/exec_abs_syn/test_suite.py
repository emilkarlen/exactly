__author__ = 'emil'

import unittest

from shelltest_test.exec_abs_syn import test_abs_syn_gen


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_abs_syn_gen.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
