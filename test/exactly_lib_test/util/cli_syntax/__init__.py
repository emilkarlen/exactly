import unittest

from exactly_lib_test.util.cli_syntax.elements import argument
from exactly_lib_test.util.cli_syntax.render import cli_program_syntax


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument.suite())
    ret_val.addTest(cli_program_syntax.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
