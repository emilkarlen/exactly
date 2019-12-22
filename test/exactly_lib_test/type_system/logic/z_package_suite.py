import unittest

from exactly_lib_test.type_system.logic.program import z_package_suite as program
from exactly_lib_test.type_system.logic.string_transformer import z_package_suite as string_transformer
from exactly_lib_test.type_system.logic.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        string_transformer.suite(),
        program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
