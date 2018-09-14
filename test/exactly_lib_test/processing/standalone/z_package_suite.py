import unittest

from exactly_lib_test.processing.standalone import fail_due_to_syntax_error_in_suite, config_only_available_in_suite


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        fail_due_to_syntax_error_in_suite.suite(),
        config_only_available_in_suite.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
