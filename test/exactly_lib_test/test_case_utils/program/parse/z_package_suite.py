import unittest

from exactly_lib_test.test_case_utils.program.parse import \
    parse_arguments, \
    parse_executable_file_executable, \
    parse_system_program, \
    parse_with_reference_to_program, parse_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_arguments.suite(),
        parse_executable_file_executable.suite(),
        parse_system_program.suite(),
        parse_with_reference_to_program.suite(),
        parse_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())