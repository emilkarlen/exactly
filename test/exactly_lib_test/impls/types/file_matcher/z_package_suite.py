import unittest

from exactly_lib_test.impls.types.file_matcher import file_type, std_expr, \
    contents_of_file
from exactly_lib_test.impls.types.file_matcher.contents_of_dir import z_package_suite as contents_of_dir
from exactly_lib_test.impls.types.file_matcher.names import z_package_suite as names
from exactly_lib_test.impls.types.file_matcher.run_program import z_package_suite as run_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        std_expr.suite(),
        names.suite(),
        file_type.suite(),
        contents_of_file.suite(),
        contents_of_dir.suite(),
        run_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
