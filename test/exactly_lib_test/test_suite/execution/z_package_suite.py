import unittest

from exactly_lib_test.test_suite.execution import execution_basics, env_vars_should_not_leak_between_cases, \
    symbol_defs_should_not_leak_between_cases, test_case_file_paths_given_to_test_case_processor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_case_file_paths_given_to_test_case_processor.suite(),
        execution_basics.suite(),
        env_vars_should_not_leak_between_cases.suite(),
        symbol_defs_should_not_leak_between_cases.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
