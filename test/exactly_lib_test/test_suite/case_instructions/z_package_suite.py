import unittest

from exactly_lib_test.test_suite.case_instructions import setup, before_assert


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        setup.suite(),
        before_assert.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
