import unittest

from exactly_lib_test.type_system_values.test_resources_test import concrete_path_part


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(concrete_path_part.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
