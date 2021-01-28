import unittest

from exactly_lib_test.impls.types.string_source.parse import contents_from_string, contents_from_file, within_parens
from exactly_lib_test.impls.types.string_source.parse.contents_from_program import \
    z_package_suite as contents_from_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        contents_from_string.suite(),
        contents_from_file.suite(),
        contents_from_program.suite(),
        within_parens.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
