import unittest

from exactly_lib_test.cli.program_modes.symbol import \
    invalid_command_line_arguments, \
    standalone_case, part_of_suite


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_command_line_arguments.suite(),
        standalone_case.suite(),
        part_of_suite.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
