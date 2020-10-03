import unittest

from exactly_lib_test.test_case_utils.file_matcher.names.name import z_package_suite as name
from exactly_lib_test.test_case_utils.file_matcher.names.path import z_package_suite as path
from exactly_lib_test.test_case_utils.file_matcher.names.stem import z_package_suite as stem
from exactly_lib_test.test_case_utils.file_matcher.names.suffix import z_package_suite as suffix
from exactly_lib_test.test_case_utils.file_matcher.names.suffixes import z_package_suite as suffixes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        path.suite(),
        name.suite(),
        stem.suite(),
        suffixes.suite(),
        suffix.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
