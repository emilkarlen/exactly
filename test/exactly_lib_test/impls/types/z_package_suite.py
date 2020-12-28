import unittest

from exactly_lib_test.impls.types.expression import z_package_suite as expression
from exactly_lib_test.impls.types.file_matcher import z_package_suite as file_matcher
from exactly_lib_test.impls.types.files_condition import z_package_suite as files_condition
from exactly_lib_test.impls.types.files_matcher import z_package_suite as files_matcher
from exactly_lib_test.impls.types.integer import z_package_suite as integer
from exactly_lib_test.impls.types.integer_matcher import z_package_suite as integer_matcher
from exactly_lib_test.impls.types.interval import z_package_suite as interval
from exactly_lib_test.impls.types.line_matcher import z_package_suite as line_matcher
from exactly_lib_test.impls.types.logic import z_package_suite as logic
from exactly_lib_test.impls.types.matcher import z_package_suite as matcher
from exactly_lib_test.impls.types.parse import z_package_suite as parse
from exactly_lib_test.impls.types.path import z_package_suite as path
from exactly_lib_test.impls.types.program import z_package_suite as program
from exactly_lib_test.impls.types.regex import z_package_suite as regex
from exactly_lib_test.impls.types.string_ import z_package_suite as string
from exactly_lib_test.impls.types.string_matcher import z_package_suite as string_matcher
from exactly_lib_test.impls.types.string_or_path import z_package_suite as string_or_path
from exactly_lib_test.impls.types.string_source import z_package_suite as string_sources
from exactly_lib_test.impls.types.string_transformers import z_package_suite as string_transformers


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(integer.suite())
    ret_val.addTest(regex.suite())
    ret_val.addTest(expression.suite())
    ret_val.addTest(interval.suite())
    ret_val.addTest(string.suite())
    ret_val.addTest(path.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(string_or_path.suite())
    ret_val.addTest(logic.suite())
    ret_val.addTest(files_condition.suite())
    ret_val.addTest(matcher.suite())
    ret_val.addTest(integer_matcher.suite())
    ret_val.addTest(string_sources.suite())
    ret_val.addTest(line_matcher.suite())
    ret_val.addTest(string_matcher.suite())
    ret_val.addTest(file_matcher.suite())
    ret_val.addTest(files_matcher.suite())
    ret_val.addTest(string_transformers.suite())
    ret_val.addTest(program.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
