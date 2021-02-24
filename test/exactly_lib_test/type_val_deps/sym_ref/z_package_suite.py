import unittest

from exactly_lib_test.type_val_deps.sym_ref import restriction
from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.type_val_deps.sym_ref.w_str_rend_restrictions import z_package_suite as w_str_rend_restrictions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(restriction.suite())
    ret_val.addTest(w_str_rend_restrictions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
