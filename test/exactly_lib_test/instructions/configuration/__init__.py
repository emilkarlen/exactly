import unittest

from exactly_lib_test.instructions.configuration import home_case, home_act, test_case_status, actor, timeout
from exactly_lib_test.instructions.configuration import test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(test_case_status.suite())
    ret_val.addTest(home_case.suite())
    ret_val.addTest(home_act.suite())
    ret_val.addTest(actor.suite())
    ret_val.addTest(timeout.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
