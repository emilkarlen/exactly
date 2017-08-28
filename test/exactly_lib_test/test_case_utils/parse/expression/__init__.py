import unittest

from exactly_lib_test.test_case_utils.parse.expression import syntax_documentation


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(syntax_documentation.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
