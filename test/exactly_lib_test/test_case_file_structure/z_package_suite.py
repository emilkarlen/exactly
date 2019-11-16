import unittest

from exactly_lib_test.test_case_file_structure import dir_dependent_value
from exactly_lib_test.test_case_file_structure import home_directory_structure, sandbox_directory_structure
from exactly_lib_test.test_case_file_structure import path_relativity
from exactly_lib_test.test_case_file_structure import relative_path_options
from exactly_lib_test.test_case_file_structure import relativity_root
from exactly_lib_test.test_case_file_structure import relativity_validation
from exactly_lib_test.test_case_file_structure import tcds
from exactly_lib_test.test_case_file_structure.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(path_relativity.suite())
    ret_val.addTest(home_directory_structure.suite())
    ret_val.addTest(sandbox_directory_structure.suite())
    ret_val.addTest(tcds.suite())
    ret_val.addTest(relativity_root.suite())
    ret_val.addTest(dir_dependent_value.suite())
    ret_val.addTest(relative_path_options.suite())
    ret_val.addTest(relativity_validation.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
