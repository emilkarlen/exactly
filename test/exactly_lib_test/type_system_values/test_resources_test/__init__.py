import unittest

from exactly_lib_test.type_system_values.test_resources_test import string_value, list_value, \
    concrete_path_part, file_ref


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(string_value.suite())
    ret_val.addTest(concrete_path_part.suite())
    ret_val.addTest(list_value.suite())
    ret_val.addTest(file_ref.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
