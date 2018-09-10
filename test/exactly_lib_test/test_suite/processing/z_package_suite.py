import unittest

from exactly_lib_test.test_suite.processing import basic_scenarios, env_vars_should_not_leak_between_cases, \
    symbol_defs_should_not_leak_between_cases, test_case_file_paths_given_to_test_case_processor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_case_file_paths_given_to_test_case_processor.suite(),
        basic_scenarios.suite(),
        env_vars_should_not_leak_between_cases.suite(),
        symbol_defs_should_not_leak_between_cases.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
