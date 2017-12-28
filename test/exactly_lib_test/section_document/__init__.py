import unittest

from exactly_lib_test.section_document import parse
from exactly_lib_test.section_document import test_resources_test
from exactly_lib_test.section_document import test_syntax, element_builder, parser_implementations, \
    parse_source


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(test_syntax.suite())
    ret_val.addTest(element_builder.suite())
    ret_val.addTest(parse_source.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(parser_implementations.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
