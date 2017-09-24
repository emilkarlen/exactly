import unittest

from exactly_lib_test.test_suite.reporters import simple_progress_reporter, junit


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        simple_progress_reporter.suite(),
        junit.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
