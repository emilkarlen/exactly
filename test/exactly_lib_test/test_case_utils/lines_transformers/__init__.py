import unittest

from exactly_lib_test.test_case_utils.lines_transformers import parse_lines_transformer
from exactly_lib_test.test_case_utils.lines_transformers import sequence, env_vars_replacement, replace
from exactly_lib_test.test_case_utils.lines_transformers import test_resources_test
from exactly_lib_test.test_case_utils.lines_transformers import vistor


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(vistor.suite())
    # Test resources use the visitor, that is tested above
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(sequence.suite())
    ret_val.addTest(env_vars_replacement.suite())
    ret_val.addTest(replace.suite())
    ret_val.addTest(parse_lines_transformer.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
