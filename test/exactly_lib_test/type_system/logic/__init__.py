import unittest

from exactly_lib_test.type_system.logic import test_resources_test, file_matcher, line_matcher, lines_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        line_matcher.suite(),
        file_matcher.suite(),
        lines_transformer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
