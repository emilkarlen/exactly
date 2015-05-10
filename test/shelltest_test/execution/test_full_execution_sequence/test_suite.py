__author__ = 'emil'

import unittest

from shelltest_test.execution.test_full_execution_sequence import \
    test_execution_mode__normal, \
    test_execution_mode__skipped


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(test_execution_mode__normal.Test))
    ret_val.addTest(unittest.makeSuite(test_execution_mode__skipped.Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
