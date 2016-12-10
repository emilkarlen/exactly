import unittest

from exactly_lib_test.cli.program_modes.help.program_modes import test_case, test_suite, utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        utils.suite(),
        test_suite.suite(),
        test_suite.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
