import unittest

from exactly_lib_test.section_document.parser_implementations import instruction_parser_for_single_phase
from exactly_lib_test.section_document.parser_implementations import instruction_parser_using_argument_parser
from exactly_lib_test.section_document.parser_implementations import new_section_element_parser


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_parser_for_single_phase.suite())
    ret_val.addTest(instruction_parser_using_argument_parser.suite())
    ret_val.addTest(new_section_element_parser.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
