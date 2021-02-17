import unittest

from exactly_lib_test.execution.full_execution.environment import \
    test_case_env_vars, \
    current_directory, \
    process_env_vars_are_not_modified


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        current_directory.suite(),
        test_case_env_vars.suite(),
        process_env_vars_are_not_modified.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
