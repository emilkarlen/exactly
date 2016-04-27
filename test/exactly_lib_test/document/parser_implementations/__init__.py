import unittest

from exactly_lib_test.document.parser_implementations import instruction_parser_for_single_phase

from exactly_lib_test.document.parser_implementations import instruction_parser_using_argument_parser


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_parser_for_single_phase.suite())
    ret_val.addTest(instruction_parser_using_argument_parser.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
