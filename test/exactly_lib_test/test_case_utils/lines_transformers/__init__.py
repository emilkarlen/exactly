import unittest

from exactly_lib_test.test_case_utils.lines_transformers import identity, sequence, env_vars_replacement, replace, \
    select_transformer, case_converters
from exactly_lib_test.test_case_utils.lines_transformers import parse_lines_transformer
from exactly_lib_test.test_case_utils.lines_transformers import test_resources_test
from exactly_lib_test.test_case_utils.lines_transformers import vistor


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(vistor.suite())
    # Test resources use the visitor, that is tested above
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(identity.suite())
    ret_val.addTest(sequence.suite())
    ret_val.addTest(replace.suite())
    ret_val.addTest(select_transformer.suite())
    ret_val.addTest(parse_lines_transformer.suite())
    ret_val.addTest(case_converters.suite())
    ret_val.addTest(env_vars_replacement.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
