import unittest

from exactly_lib_test.test_case_utils.files_matcher.files_condition_containment import invalid_syntax, \
    validation_failure, symbol_references, common_execution_outcome, \
    specific_for_equals, specific_for_contains


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        symbol_references.suite(),
        validation_failure.suite(),
        common_execution_outcome.suite(),
        specific_for_equals.suite(),
        specific_for_contains.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
