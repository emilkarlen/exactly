import unittest

from exactly_lib_test.test_case_utils.file_matcher.names.name import common, glob_pattern, reg_ex, specific


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        specific.suite(),
        glob_pattern.suite(),
        reg_ex.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
