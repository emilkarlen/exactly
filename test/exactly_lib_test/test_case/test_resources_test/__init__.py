import unittest

from exactly_lib_test.test_case.test_resources_test import file_ref_relativity, file_ref


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(file_ref_relativity.suite())
    ret_val.addTest(file_ref.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
