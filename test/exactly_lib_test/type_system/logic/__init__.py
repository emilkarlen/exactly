import unittest

from exactly_lib_test.type_system.logic import file_matcher, line_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        line_matcher.suite(),
        file_matcher.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
