import unittest

from exactly_lib_test.processing import preprocessor
from exactly_lib_test.processing import processing_utils


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(preprocessor.suite())
    ret_val.addTest(processing_utils.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
