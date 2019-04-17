import unittest

from exactly_lib_test.processing.standalone import \
    suite_error_handling, config_only_available_in_suite, inclusion_of_case_instructions_from_suite


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_error_handling.suite(),
        inclusion_of_case_instructions_from_suite.suite(),
        config_only_available_in_suite.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
