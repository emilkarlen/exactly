import unittest

from shellcheck_lib_test.document import parse, test_syntax, parser_implementations


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse.suite())
    ret_val.addTest(test_syntax.suite())
    ret_val.addTest(parser_implementations.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
