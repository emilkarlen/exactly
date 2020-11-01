import unittest

from exactly_lib_test.type_val_prims.program import commands
from exactly_lib_test.type_val_prims.program.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        commands.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
