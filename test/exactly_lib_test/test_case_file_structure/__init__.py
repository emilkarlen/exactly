import unittest

from exactly_lib_test.test_case_file_structure import concrete_path_parts, file_refs, relativity_validation
from exactly_lib_test.test_case_file_structure import sandbox_directory_structure, relativity_root, test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(sandbox_directory_structure.suite())
    ret_val.addTest(relativity_root.suite())
    ret_val.addTest(relativity_validation.suite())
    ret_val.addTest(concrete_path_parts.suite())
    ret_val.addTest(file_refs.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
