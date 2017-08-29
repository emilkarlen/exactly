import unittest

from exactly_lib_test.test_case_utils.lines_transformers import transformers, env_vars_replacement


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(transformers.suite())
    ret_val.addTest(env_vars_replacement.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
