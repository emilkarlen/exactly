import unittest

from exactly_lib_test.instructions.before_assert.test_resources import instruction_check_test


def suite() -> unittest.TestSuite:
    return instruction_check_test.suite()
