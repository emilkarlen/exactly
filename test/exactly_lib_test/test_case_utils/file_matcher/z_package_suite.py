import unittest

from exactly_lib_test.test_case_utils.file_matcher import matching_files_in_dir
from exactly_lib_test.test_case_utils.file_matcher import name_glob_pattern, name_reg_ex, file_type, combinators, \
    contents
from exactly_lib_test.test_case_utils.file_matcher import parse_file_matcher


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        matching_files_in_dir.suite(),
        name_glob_pattern.suite(),
        name_reg_ex.suite(),
        file_type.suite(),
        combinators.suite(),
        parse_file_matcher.suite(),
        contents.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
