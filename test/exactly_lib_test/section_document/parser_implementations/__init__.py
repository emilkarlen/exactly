import unittest

from exactly_lib_test.section_document.parser_implementations import instruction_parser_for_single_phase
from exactly_lib_test.section_document.parser_implementations import instruction_parser_using_argument_parser
from exactly_lib_test.section_document.parser_implementations import new_section_element_parser
from exactly_lib_test.section_document.parser_implementations import optional_description_and_instruction_parser
from exactly_lib_test.section_document.parser_implementations import parser_for_dictionary_of_instructions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_parser_for_single_phase.suite())
    ret_val.addTest(instruction_parser_using_argument_parser.suite())
    ret_val.addTest(new_section_element_parser.suite())
    ret_val.addTest(optional_description_and_instruction_parser.suite())
    ret_val.addTest(parser_for_dictionary_of_instructions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
