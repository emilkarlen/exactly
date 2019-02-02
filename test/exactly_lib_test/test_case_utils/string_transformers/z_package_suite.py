import unittest

from exactly_lib_test.test_case_utils.string_transformers import env_vars_replacement, replace, \
    select_transformer, case_converters, sequence
from exactly_lib_test.test_case_utils.string_transformers import \
    parse_string_transformer, vistor
from exactly_lib_test.test_case_utils.string_transformers.test_resources_test import \
    z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(vistor.suite())
    # Test resources use the visitor, that is tested above
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(replace.suite())
    ret_val.addTest(select_transformer.suite())
    ret_val.addTest(sequence.suite())
    ret_val.addTest(parse_string_transformer.suite())
    ret_val.addTest(case_converters.suite())
    ret_val.addTest(env_vars_replacement.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
