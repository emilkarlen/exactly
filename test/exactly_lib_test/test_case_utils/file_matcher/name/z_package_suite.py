import unittest

from exactly_lib_test.test_case_utils.file_matcher.name import glob_pattern, reg_ex


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        glob_pattern.suite(),
        reg_ex.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
