import unittest

from exactly_lib_test.section_document import element_builder
from exactly_lib_test.section_document import source_location
from exactly_lib_test.section_document import test_syntax, \
    parse_source, parsed_section_element, exceptions
from exactly_lib_test.section_document.document_parser import z_package_suite as document_parser
from exactly_lib_test.section_document.element_parsers import z_package_suite as element_parsers
from exactly_lib_test.section_document.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        exceptions.suite(),
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
