import unittest

from exactly_lib_test.cli.program_modes.symbol.individual import definition, references


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        definition.suite(),
        references.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
