import unittest

from exactly_lib_test.section_document.element_parsers import instruction_parsers
from exactly_lib_test.section_document.element_parsers import misc_utils
from exactly_lib_test.section_document.element_parsers import optional_description_and_instruction_parser
from exactly_lib_test.section_document.element_parsers import parser_for_dictionary_of_instructions
from exactly_lib_test.section_document.element_parsers import section_element_parsers
from exactly_lib_test.section_document.element_parsers import token_parse, token_stream
from exactly_lib_test.section_document.element_parsers import token_stream_parser
from exactly_lib_test.section_document.element_parsers.ps_or_tp import z_package_suite as ps_or_tp
from exactly_lib_test.section_document.element_parsers.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(section_element_parsers.suite())
    ret_val.addTest(optional_description_and_instruction_parser.suite())
    ret_val.addTest(parser_for_dictionary_of_instructions.suite())
    ret_val.addTest(token_parse.suite())
    ret_val.addTest(token_stream.suite())
    ret_val.addTest(token_stream_parser.suite())
    ret_val.addTest(instruction_parsers.suite())
    ret_val.addTest(ps_or_tp.suite())
    ret_val.addTest(misc_utils.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
