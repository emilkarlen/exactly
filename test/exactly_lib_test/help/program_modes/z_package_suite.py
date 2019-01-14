import unittest

from exactly_lib_test.help.program_modes.common import z_package_suite as common
from exactly_lib_test.help.program_modes.help import z_package_suite as help_
from exactly_lib_test.help.program_modes.symbol import z_package_suite as symbol
from exactly_lib_test.help.program_modes.test_case import z_package_suite as test_case
from exactly_lib_test.help.program_modes.test_suite import z_package_suite as test_suite


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(common.suite())
    ret_val.addTest(test_case.suite())
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(symbol.suite())
    ret_val.addTest(help_.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
