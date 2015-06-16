import unittest

from shellcheck_lib_test.cli import argument_parsing
from shellcheck_lib_test.cli.default import test_suite as default_test_suite


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    ret_val.addTest(default_test_suite.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
