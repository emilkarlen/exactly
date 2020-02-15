import unittest

from exactly_lib_test.test_case_utils.files_condition import invalid_syntax


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
