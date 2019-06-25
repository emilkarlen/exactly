import unittest

from exactly_lib_test.cli.program_modes.symbol.all import part_of_suite, preprocessed_case, standalone_file


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        standalone_file.suite(),
        part_of_suite.suite(),
        preprocessed_case.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
