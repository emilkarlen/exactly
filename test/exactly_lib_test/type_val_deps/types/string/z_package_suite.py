import unittest

from exactly_lib_test.type_val_deps.types.string import string_ddv, string_sdv, string_sdvs
from exactly_lib_test.type_val_deps.types.string.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        string_ddv.suite(),
        string_sdv.suite(),
        string_sdvs.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
