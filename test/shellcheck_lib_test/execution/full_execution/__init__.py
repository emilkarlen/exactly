import unittest

from shellcheck_lib_test.execution.full_execution import execution_mode
from shellcheck_lib_test.execution.full_execution import \
    test_translation_of_partial_result_to_full_result, \
    test_environment


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(test_translation_of_partial_result_to_full_result.Test))
    ret_val.addTest(unittest.makeSuite(test_environment.Test))
    ret_val.addTest(execution_mode.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
