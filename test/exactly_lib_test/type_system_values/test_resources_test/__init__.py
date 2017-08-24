import unittest

from exactly_lib_test.type_system_values.test_resources_test import string_value_assertions, list_value_assertions, \
    path_part_assertions, file_ref_assertions, \
    file_selector_assertions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(string_value_assertions.suite())
    ret_val.addTest(path_part_assertions.suite())
    ret_val.addTest(list_value_assertions.suite())
    ret_val.addTest(file_ref_assertions.suite())
    ret_val.addTest(file_selector_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
