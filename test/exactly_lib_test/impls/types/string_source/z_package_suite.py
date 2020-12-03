import unittest

from exactly_lib_test.impls.types.string_source import source_from_lines_base, source_of_file, command_output
from exactly_lib_test.impls.types.string_source.parse import z_package_suite as parse


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        source_from_lines_base.suite(),
        source_of_file.suite(),
        command_output.suite(),
        parse.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
