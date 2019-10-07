import unittest

from exactly_lib_test.cli.program_modes.symbol.individual.definition import main_program_execution


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        main_program_execution.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
