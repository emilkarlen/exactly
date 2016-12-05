import unittest

from exactly_lib_test.util import functional, line_source, textformat, tables, cli_syntax


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(functional.suite())
    ret_val.addTest(tables.suite())
    ret_val.addTest(line_source.suite())
    ret_val.addTest(textformat.suite())
    ret_val.addTest(cli_syntax.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
