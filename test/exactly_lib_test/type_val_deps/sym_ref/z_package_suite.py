import unittest

from exactly_lib_test.type_val_deps.sym_ref import value_restrictions, reference_restrictions, restriction, \
    restriction_failures
from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(value_restrictions.suite())
    ret_val.addTest(restriction.suite())
    ret_val.addTest(reference_restrictions.suite())
    ret_val.addTest(restriction_failures.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
