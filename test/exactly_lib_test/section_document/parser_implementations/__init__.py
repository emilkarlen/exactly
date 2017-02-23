import unittest

from exactly_lib_test.section_document.parser_implementations import new_section_element_parser
from exactly_lib_test.section_document.parser_implementations import optional_description_and_instruction_parser
from exactly_lib_test.section_document.parser_implementations import parser_for_dictionary_of_instructions
from exactly_lib_test.section_document.parser_implementations import token_parse


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(new_section_element_parser.suite())
    ret_val.addTest(optional_description_and_instruction_parser.suite())
    ret_val.addTest(parser_for_dictionary_of_instructions.suite())
    ret_val.addTest(token_parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
