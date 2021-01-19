import unittest

from exactly_lib_test.impls.types.program import parse_arguments, parse_executable_file_path, parse_system_program, \
    parse_with_reference_to_program
from exactly_lib_test.impls.types.program.parse_program import z_package_suite as parse_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_arguments.suite(),
        parse_executable_file_path.suite(),
        parse_system_program.suite(),
        parse_with_reference_to_program.suite(),
        parse_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
