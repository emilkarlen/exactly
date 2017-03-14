import unittest

from exactly_lib_test.test_case import error_description
from exactly_lib_test.test_case import file_refs
from exactly_lib_test.test_case import phases
from exactly_lib_test.test_case import test_resources_test
from exactly_lib_test.test_case import value_definition


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(error_description.suite())
    ret_val.addTest(phases.suite())
    ret_val.addTest(file_refs.suite())
    ret_val.addTest(value_definition.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
