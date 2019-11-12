import unittest

from exactly_lib_test.type_system.data import concrete_path_parts, paths, list_ddv, string_ddv
from exactly_lib_test.type_system.data import path_description
from exactly_lib_test.type_system.data.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(path_description.suite())
    ret_val.addTest(concrete_path_parts.suite())
    ret_val.addTest(paths.suite())
    ret_val.addTest(string_ddv.suite())
    ret_val.addTest(list_ddv.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
