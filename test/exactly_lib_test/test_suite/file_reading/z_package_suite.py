import unittest

from exactly_lib_test.test_suite.file_reading import exception, suite_hierarchy_reading


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        exception.suite(),
        suite_hierarchy_reading.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
