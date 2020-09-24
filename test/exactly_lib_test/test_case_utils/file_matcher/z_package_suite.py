import unittest

from exactly_lib_test.test_case_utils.file_matcher import file_type, std_expr, \
    contents_of_file
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir import z_package_suite as contents_of_dir
from exactly_lib_test.test_case_utils.file_matcher.name import z_package_suite as name
from exactly_lib_test.test_case_utils.file_matcher.path import z_package_suite as path
from exactly_lib_test.test_case_utils.file_matcher.run_program import z_package_suite as run_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        std_expr.suite(),
        name.suite(),
        path.suite(),
        file_type.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
        run_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
