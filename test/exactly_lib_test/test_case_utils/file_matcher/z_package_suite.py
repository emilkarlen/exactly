import unittest

from exactly_lib_test.test_case_utils.file_matcher import matching_files_in_dir
from exactly_lib_test.test_case_utils.file_matcher import name_glob_pattern, name_reg_ex, file_type, std_expr, \
    contents_of_file, contents_of_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        std_expr.suite(),
        matching_files_in_dir.suite(),
        name_glob_pattern.suite(),
        name_reg_ex.suite(),
        file_type.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
