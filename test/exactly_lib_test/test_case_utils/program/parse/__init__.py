import unittest

from exactly_lib_test.test_case_utils.program.parse import parse_executable_file_executable, \
    parse_with_reference_to_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_executable_file_executable.suite(),
        parse_with_reference_to_program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
