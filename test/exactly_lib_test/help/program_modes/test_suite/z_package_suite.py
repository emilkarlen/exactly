import unittest

from exactly_lib_test.help.program_modes.test_suite import cli_syntax


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(cli_syntax.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
