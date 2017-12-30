import unittest

from exactly_lib_test.section_document import test_resources_test, parse
from exactly_lib_test.section_document import test_syntax, parser_implementations, \
    parse_source, section_element_parser


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(section_element_parser.suite())
    ret_val.addTest(test_syntax.suite())
    ret_val.addTest(parse_source.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(parser_implementations.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
