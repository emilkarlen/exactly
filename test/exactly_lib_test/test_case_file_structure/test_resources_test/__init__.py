import unittest

from exactly_lib_test.test_case_file_structure.test_resources_test import concrete_path_part, path_relativity, \
    file_ref


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_relativity.suite())
    ret_val.addTest(concrete_path_part.suite())
    ret_val.addTest(file_ref.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
