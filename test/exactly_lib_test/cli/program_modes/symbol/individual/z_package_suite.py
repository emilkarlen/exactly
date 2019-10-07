import unittest

from exactly_lib_test.cli.program_modes.symbol.individual import references
from exactly_lib_test.cli.program_modes.symbol.individual.definition import z_package_suite as definition


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        definition.suite(),
        references.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
