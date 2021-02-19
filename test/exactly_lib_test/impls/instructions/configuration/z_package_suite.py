import unittest

from exactly_lib_test.impls.instructions.configuration import hds_case, hds_act, test_case_status
from exactly_lib_test.impls.instructions.configuration.actor import z_package_suite as actor
from exactly_lib_test.impls.instructions.configuration.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(test_case_status.suite())
    ret_val.addTest(hds_case.suite())
    ret_val.addTest(hds_act.suite())
    ret_val.addTest(actor.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
