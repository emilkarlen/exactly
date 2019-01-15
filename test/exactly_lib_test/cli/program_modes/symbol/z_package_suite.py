import unittest

from exactly_lib_test.cli.program_modes.symbol import \
    invalid_command_line_arguments, individual
from exactly_lib_test.cli.program_modes.symbol.all import z_package_suite as all


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_command_line_arguments.suite(),
        all.suite(),
        individual.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
