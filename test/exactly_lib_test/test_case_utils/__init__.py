import unittest

from exactly_lib_test.test_case_utils import expression, condition
from exactly_lib_test.test_case_utils import file_properties, parse
from exactly_lib_test.test_case_utils import line_matcher, string_transformers, file_matcher, program


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(expression.suite())
    ret_val.addTest(condition.suite())
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(line_matcher.suite())
    ret_val.addTest(file_matcher.suite())
    ret_val.addTest(string_transformers.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(program.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
