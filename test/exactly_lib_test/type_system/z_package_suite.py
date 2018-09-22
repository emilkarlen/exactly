import unittest

from exactly_lib_test.type_system import utils
from exactly_lib_test.type_system.data import z_package_suite as data
from exactly_lib_test.type_system.logic import z_package_suite as logic


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(utils.suite())
    ret_val.addTest(data.suite())
    ret_val.addTest(logic.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
