import unittest

from shelltest_test.execution.test_full_execution_sequence import \
    test_execution_mode__normal, \
    test_execution_mode__skipped, \
    test_execution_mode__xfail, \
    test_translation_of_partial_result_to_full_result


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(test_translation_of_partial_result_to_full_result.Test))
    ret_val.addTest(unittest.makeSuite(test_execution_mode__normal.Test))
    ret_val.addTest(unittest.makeSuite(test_execution_mode__skipped.Test))
    ret_val.addTest(unittest.makeSuite(test_execution_mode__xfail.Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
