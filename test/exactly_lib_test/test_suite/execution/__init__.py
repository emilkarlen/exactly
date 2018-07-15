import unittest

from exactly_lib_test.test_suite.execution import execution_basics, propagation_of_case_instructions, \
    env_vars_should_not_leak_between_cases


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        execution_basics.suite(),
        propagation_of_case_instructions.suite(),
        env_vars_should_not_leak_between_cases.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
