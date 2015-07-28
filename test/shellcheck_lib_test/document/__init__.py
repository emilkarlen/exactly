import unittest

from shellcheck_lib_test.document import parse2, test_syntax


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse2.suite())
    ret_val.addTest(test_syntax.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
