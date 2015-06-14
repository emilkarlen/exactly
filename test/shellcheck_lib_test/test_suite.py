import unittest

from shellcheck_lib_test.general import test_suite as general_test
from shellcheck_lib_test.document import test_suite as document_test
from shellcheck_lib_test.test_case import test_suite as test_case_test
from shellcheck_lib_test.execution import test_suite as execution_test
from shellcheck_lib_test.cli import test_suite as cli_test
from shellcheck_lib_test.instructions import test_suite as instructions_test


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(general_test.suite())
    ret_val.addTest(document_test.suite())
    ret_val.addTest(test_case_test.suite())
    ret_val.addTest(execution_test.suite())
    ret_val.addTest(cli_test.suite())
    ret_val.addTest(instructions_test.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
