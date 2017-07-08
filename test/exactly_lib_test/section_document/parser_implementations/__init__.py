import unittest

from exactly_lib_test.section_document.parser_implementations import optional_description_and_instruction_parser
from exactly_lib_test.section_document.parser_implementations import parser_for_dictionary_of_instructions
from exactly_lib_test.section_document.parser_implementations import section_element_parsers
from exactly_lib_test.section_document.parser_implementations import test_resources_test
from exactly_lib_test.section_document.parser_implementations import token_parse, token_stream


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(section_element_parsers.suite())
    ret_val.addTest(optional_description_and_instruction_parser.suite())
    ret_val.addTest(parser_for_dictionary_of_instructions.suite())
    ret_val.addTest(token_parse.suite())
    ret_val.addTest(token_stream.suite())
    ret_val.addTest(test_resources_test.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
