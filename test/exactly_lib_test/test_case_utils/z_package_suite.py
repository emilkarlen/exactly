import unittest

from exactly_lib_test.test_case_utils import file_properties
from exactly_lib_test.test_case_utils import return_svh_via_exceptions
from exactly_lib_test.test_case_utils.condition import z_package_suite as condition
from exactly_lib_test.test_case_utils.expression import z_package_suite as expression
from exactly_lib_test.test_case_utils.file_matcher import z_package_suite as file_matcher
from exactly_lib_test.test_case_utils.line_matcher import z_package_suite as line_matcher
from exactly_lib_test.test_case_utils.parse import z_package_suite as parse
from exactly_lib_test.test_case_utils.program import z_package_suite as program
from exactly_lib_test.test_case_utils.regex import z_package_suite as regex
from exactly_lib_test.test_case_utils.string_matcher import z_package_suite as string_matcher
from exactly_lib_test.test_case_utils.string_transformers import z_package_suite as string_transformers


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(return_svh_via_exceptions.suite())
    ret_val.addTest(expression.suite())
    ret_val.addTest(condition.suite())
    ret_val.addTest(regex.suite())
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(line_matcher.suite())
    ret_val.addTest(string_matcher.suite())
    ret_val.addTest(file_matcher.suite())
    ret_val.addTest(string_transformers.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(program.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
