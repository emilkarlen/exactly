import unittest

from exactly_lib_test.instructions.utils.arg_parse import symbol_, parse_utils, \
    parse_string, parse_file_ref, parse_here_document, \
    parse_executable_file, \
    parse_here_doc_or_file_ref


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse_utils.suite())
    ret_val.addTest(symbol_.suite())
    ret_val.addTest(parse_string.suite())
    ret_val.addTest(parse_file_ref.suite())
    ret_val.addTest(parse_here_document.suite())
    ret_val.addTest(parse_executable_file.suite())
    ret_val.addTest(parse_here_doc_or_file_ref.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
