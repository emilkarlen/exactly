import unittest

from shellcheck_lib_test.execution.full_execution import \
    test_execution_mode__normal, \
    test_execution_mode__skipped, \
    test_execution_mode__xfail, \
    test_translation_of_partial_result_to_full_result, \
    test_environment


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(test_translation_of_partial_result_to_full_result.Test))
    ret_val.addTest(test_execution_mode__normal.suite())
    ret_val.addTest(unittest.makeSuite(test_execution_mode__skipped.Test))
    ret_val.addTest(unittest.makeSuite(test_execution_mode__xfail.Test))
    ret_val.addTest(unittest.makeSuite(test_environment.Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
