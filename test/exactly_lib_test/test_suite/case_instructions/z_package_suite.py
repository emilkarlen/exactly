import unittest

from exactly_lib_test.test_suite.case_instructions import propagation_of_case_instructions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        propagation_of_case_instructions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
