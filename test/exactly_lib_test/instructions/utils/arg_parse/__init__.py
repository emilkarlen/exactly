import unittest

from exactly_lib_test.instructions.utils.arg_parse import parse_file_ref, parse_utils, parse_destination_path
from exactly_lib_test.instructions.utils.arg_parse import parse_here_document, parse_executable_file


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse_utils.suite())
    ret_val.addTest(parse_destination_path.suite())
    ret_val.addTest(parse_file_ref.suite())
    ret_val.addTest(parse_here_document.suite())
    ret_val.addTest(parse_executable_file.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
