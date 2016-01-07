import unittest

from shellcheck_lib_test.instructions.before_assert.test_resources import instruction_check_test


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_check_test.suite())
    return ret_val
