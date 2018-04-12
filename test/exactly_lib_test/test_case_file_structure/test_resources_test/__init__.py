import unittest

from exactly_lib_test.test_case_file_structure.test_resources_test import \
    dir_dependent_value, dir_dep_value_assertions, \
    path_relativity, home_populators, hds_utils


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_relativity.suite())
    ret_val.addTest(dir_dependent_value.suite())
    ret_val.addTest(dir_dep_value_assertions.suite())
    ret_val.addTest(home_populators.suite())
    ret_val.addTest(hds_utils.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
