import unittest

from exactly_lib_test.type_system_values.file_transformers import env_vars_replacement


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(env_vars_replacement.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
