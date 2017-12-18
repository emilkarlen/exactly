import unittest

from exactly_lib_test.test_suite.execution import execution_basics, propagation_of_case_instructions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        execution_basics.suite(),
        propagation_of_case_instructions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
