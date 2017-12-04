import unittest

from exactly_lib_test.test_case_utils import expression, condition
from exactly_lib_test.test_case_utils import file_properties, sub_process_execution, parse
from exactly_lib_test.test_case_utils import line_matcher, lines_transformers, file_matcher


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(expression.suite())
    condition.suite(),
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(sub_process_execution.suite())
    ret_val.addTest(line_matcher.suite())
    ret_val.addTest(file_matcher.suite())
    ret_val.addTest(lines_transformers.suite())
    ret_val.addTest(parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
