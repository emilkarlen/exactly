import unittest

from exactly_lib_test.value_definition import test_resources_test, file_ref_with_val_def
from exactly_lib_test.value_definition import value_definition, value_structure, concrete_values


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(value_structure.suite())
    ret_val.addTest(concrete_values.suite())
    ret_val.addTest(file_ref_with_val_def.suite())
    ret_val.addTest(value_definition.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
