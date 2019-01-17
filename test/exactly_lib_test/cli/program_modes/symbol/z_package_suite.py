import unittest

from exactly_lib_test.cli.program_modes.symbol import \
    invalid_command_line_arguments
from exactly_lib_test.cli.program_modes.symbol.all import z_package_suite as all_
from exactly_lib_test.cli.program_modes.symbol.individual import z_package_suite as individual


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_command_line_arguments.suite(),
        all_.suite(),
        individual.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
