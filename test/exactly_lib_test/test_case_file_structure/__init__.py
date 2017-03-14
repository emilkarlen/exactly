import unittest

from exactly_lib_test.test_case_file_structure import file_refs
from exactly_lib_test.test_case_file_structure import sandbox_directory_structure, test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(sandbox_directory_structure.suite())
    ret_val.addTest(file_refs.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
