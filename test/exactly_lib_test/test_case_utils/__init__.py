import unittest

from exactly_lib_test.test_case_utils import file_properties, sub_process_execution
from exactly_lib_test.test_case_utils import parse


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(sub_process_execution.suite())
    ret_val.addTest(parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
