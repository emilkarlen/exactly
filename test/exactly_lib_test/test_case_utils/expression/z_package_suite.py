import unittest

from exactly_lib_test.test_case_utils.expression import parser
from exactly_lib_test.test_case_utils.expression import syntax_documentation


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(syntax_documentation.suite())
    ret_val.addTest(parser.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
