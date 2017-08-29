import unittest

from exactly_lib_test.test_case_utils import expression
from exactly_lib_test.test_case_utils import file_properties, sub_process_execution, parse
from exactly_lib_test.test_case_utils import lines_transformers, file_selectors
from exactly_lib_test.test_case_utils import test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(expression.suite())
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(sub_process_execution.suite())
    ret_val.addTest(lines_transformers.suite())
    ret_val.addTest(file_selectors.suite())
    ret_val.addTest(parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
