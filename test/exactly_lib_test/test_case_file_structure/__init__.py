import unittest

from exactly_lib_test.test_case_file_structure import sandbox_directory_structure


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(sandbox_directory_structure.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
