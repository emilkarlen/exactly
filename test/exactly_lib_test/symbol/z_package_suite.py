import unittest

from exactly_lib_test.symbol import restriction, data, symbol_syntax
from exactly_lib_test.symbol.data import z_package_suite as data
from exactly_lib_test.symbol.err_msg import z_package_suite as err_msg
from exactly_lib_test.symbol.logic import z_package_suite as logic
from exactly_lib_test.symbol.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        symbol_syntax.suite(),
        err_msg.suite(),
        restriction.suite(),
        data.suite(),
        logic.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
