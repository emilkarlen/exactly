import unittest

from exactly_lib_test.cli.program_modes.symbol import \
    invalid_command_line_arguments, invalid_file_contents_syntax, \
    successful_scenarios


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_command_line_arguments.suite(),
        invalid_file_contents_syntax.suite(),
        successful_scenarios.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
