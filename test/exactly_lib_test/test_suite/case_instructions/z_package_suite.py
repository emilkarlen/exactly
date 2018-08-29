import unittest

from exactly_lib_test.test_suite.case_instructions import setup, assert_, before_assert, cleanup


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        setup.suite(),
        before_assert.suite(),
        assert_.suite(),
        cleanup.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
