import unittest

from exactly_lib_test.test_suite.case_instructions import configuration, setup, assert_, before_assert, cleanup, act


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        configuration.suite(),
        setup.suite(),
        act.suite(),
        before_assert.suite(),
        assert_.suite(),
        cleanup.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
