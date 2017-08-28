import unittest

from exactly_lib_test.test_case_utils.parse import expression_parser, parse_file_selector
from exactly_lib_test.test_case_utils.parse import symbol_syntax, misc_utils, parse_string, parse_here_document, \
    parse_list, parse_file_ref, parse_here_doc_or_file_ref


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(misc_utils.suite())
    ret_val.addTest(symbol_syntax.suite())
    ret_val.addTest(parse_string.suite())
    ret_val.addTest(parse_list.suite())
    ret_val.addTest(parse_file_ref.suite())
    ret_val.addTest(parse_here_document.suite())
    ret_val.addTest(parse_here_doc_or_file_ref.suite())
    ret_val.addTest(expression_parser.suite())
    ret_val.addTest(parse_file_selector.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
