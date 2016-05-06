import unittest

from exactly_lib_test.help.program_modes.test_case import contents, main_documentation, cli_syntax


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(main_documentation.suite())
    ret_val.addTest(contents.suite())
    ret_val.addTest(cli_syntax.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
