import unittest

from exactly_lib_test.instructions.configuration import home, act_home, test_case_status, actor, timeout
from exactly_lib_test.instructions.configuration import test_resources


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(test_case_status.suite())
    ret_val.addTest(home.suite())
    ret_val.addTest(act_home.suite())
    ret_val.addTest(actor.suite())
    ret_val.addTest(timeout.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
