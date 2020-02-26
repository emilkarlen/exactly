import unittest

from exactly_lib_test.test_case_utils.files_matcher.files_condition_containment import invalid_syntax, \
    validation_failure


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        validation_failure.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
