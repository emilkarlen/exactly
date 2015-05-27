import unittest

from shelltest_test.general import test_suite as general_test
from shelltest_test.document import test_suite as document_test
from shelltest_test.test_case import test_suite as test_case_test
from shelltest_test.execution import test_suite as execution_test
from shelltest_test.cli import test_suite as cli_test


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(general_test.suite())
    ret_val.addTest(document_test.suite())
    ret_val.addTest(test_case_test.suite())
    ret_val.addTest(execution_test.suite())
    ret_val.addTest(cli_test.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
