import unittest

from exactly_lib_test.type_val_deps.test_resources_test.any_ import z_package_suite as any_
from exactly_lib_test.type_val_deps.test_resources_test.w_str_rend import z_package_suite as data


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        data.suite(),
        any_.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
