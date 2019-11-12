import unittest

from exactly_lib_test.type_system.data.test_resources_test import string_value_assertions, \
    list_ddv_assertions, path_part_assertions, path_assertions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(string_value_assertions.suite())
    ret_val.addTest(list_ddv_assertions.suite())
    ret_val.addTest(path_part_assertions.suite())
    ret_val.addTest(path_assertions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
