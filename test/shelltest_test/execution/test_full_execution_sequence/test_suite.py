__author__ = 'emil'

import unittest

from shelltest_test.execution.test_full_execution_sequence import \
    test_normal_execution_mode, \
    test_nonnormal_execution_mode


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(test_normal_execution_mode.Test))
    ret_val.addTest(unittest.makeSuite(test_nonnormal_execution_mode.Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
