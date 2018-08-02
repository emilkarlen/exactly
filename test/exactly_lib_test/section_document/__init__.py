import unittest

from exactly_lib_test.section_document import element_builder
from exactly_lib_test.section_document import source_location
from exactly_lib_test.section_document import test_resources_test, document_parser
from exactly_lib_test.section_document import test_syntax, element_parsers, \
    parse_source, parsed_section_element


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        source_location.suite(),
        test_resources_test.suite(),
        parsed_section_element.suite(),
        test_syntax.suite(),
        element_builder.suite(),
        parse_source.suite(),
        document_parser.suite(),
        element_parsers.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
