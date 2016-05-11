import unittest

from exactly_lib_test.instructions.utils.arg_parse import parse_file_ref, parse_utils
from exactly_lib_test.instructions.utils.arg_parse import parse_here_document


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse_utils.suite())
    ret_val.addTest(parse_file_ref.suite())
    ret_val.addTest(parse_here_document.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
