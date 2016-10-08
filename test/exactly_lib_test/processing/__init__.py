import unittest

from exactly_lib_test.processing import preprocessor
from exactly_lib_test.processing import processing_utils
from exactly_lib_test.processing.parse import source_parser_and_instruction


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(preprocessor.suite())
    ret_val.addTest(processing_utils.suite())
    ret_val.addTest(source_parser_and_instruction.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
