import unittest

from exactly_lib_test.test_case_utils.file_matcher import name_glob_pattern, name_reg_ex, file_type, std_expr, \
    contents_of_file
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir import z_package_suite as contents_of_dir
from exactly_lib_test.test_case_utils.file_matcher.run_program import z_package_suite as run_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        std_expr.suite(),
        name_glob_pattern.suite(),
        name_reg_ex.suite(),
        file_type.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
        run_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
