import unittest

from exactly_lib_test.type_system_values import concrete_path_parts
from exactly_lib_test.type_system_values import file_refs
from exactly_lib_test.type_system_values import test_resources_test, string_value, list_value


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(concrete_path_parts.suite())
    ret_val.addTest(file_refs.suite())
    ret_val.addTest(string_value.suite())
    ret_val.addTest(list_value.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
