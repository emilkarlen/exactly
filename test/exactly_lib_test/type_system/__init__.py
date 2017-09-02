import unittest

from exactly_lib_test.type_system import test_resources_test
from exactly_lib_test.type_system import utils
from exactly_lib_test.type_system.data import concrete_path_parts, file_refs, list_value, string_value


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(utils.suite())
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(concrete_path_parts.suite())
    ret_val.addTest(file_refs.suite())
    ret_val.addTest(string_value.suite())
    ret_val.addTest(list_value.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
