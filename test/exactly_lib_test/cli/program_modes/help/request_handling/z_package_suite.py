import unittest

from exactly_lib_test.cli.program_modes.help.request_handling import console_help


def suite() -> unittest.TestSuite:
    return console_help.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
