import unittest

from exactly_lib_test.test_case import error_description
from exactly_lib_test.test_case import phases
from exactly_lib_test.test_case import sandbox_directory_structure


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(error_description.suite())
    ret_val.addTest(phases.suite())
    ret_val.addTest(sandbox_directory_structure.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
