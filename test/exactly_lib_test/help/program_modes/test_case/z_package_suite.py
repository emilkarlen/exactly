import unittest

from exactly_lib_test.help.program_modes.test_case import render, specification, cli_syntax


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(specification.suite())
    ret_val.addTest(render.suite())
    ret_val.addTest(cli_syntax.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
