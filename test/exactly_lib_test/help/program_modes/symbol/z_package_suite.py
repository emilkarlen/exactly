import unittest

from exactly_lib_test.help.program_modes.symbol import cli_syntax


def suite() -> unittest.TestSuite:
    return cli_syntax.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
