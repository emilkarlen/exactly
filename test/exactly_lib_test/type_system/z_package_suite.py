import unittest

from exactly_lib_test.type_system.logic import z_package_suite as logic
from exactly_lib_test.type_system.trace import z_package_suite as trace


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(trace.suite())
    ret_val.addTest(logic.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
