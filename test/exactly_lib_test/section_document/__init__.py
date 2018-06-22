import unittest

from exactly_lib_test.section_document import element_builder
from exactly_lib_test.section_document import test_resources_test, document_parser
from exactly_lib_test.section_document import test_syntax, element_parsers, \
    parse_source, parsed_section_element


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(parsed_section_element.suite())
    ret_val.addTest(test_syntax.suite())
    ret_val.addTest(element_builder.suite())
    ret_val.addTest(parse_source.suite())
    ret_val.addTest(document_parser.suite())
    ret_val.addTest(element_parsers.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
