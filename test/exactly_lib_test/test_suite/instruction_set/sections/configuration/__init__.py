import unittest

from exactly_lib_test.test_suite.instruction_set.sections.configuration import preprocessor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        preprocessor.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
