import unittest

from exactly_lib_test.cli.program_modes.symbol.all import part_of_suite, preprocessed_case, standalone_file, \
    standalone_case, standalone_suite


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        standalone_file.suite(),
        standalone_case.suite(),
        standalone_suite.suite(),
        part_of_suite.suite(),
        preprocessed_case.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
