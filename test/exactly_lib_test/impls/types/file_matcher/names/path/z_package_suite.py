import unittest

from exactly_lib_test.impls.types.file_matcher.names.path import common, glob_pattern, reg_ex


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        glob_pattern.suite(),
        reg_ex.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
