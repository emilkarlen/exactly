import unittest

from shellcheck_lib_test.document import test_parse, test_syntax


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_parse.suite())
    ret_val.addTest(test_syntax.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
