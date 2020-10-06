import unittest

from exactly_lib_test.type_system.logic.string_model import from_lines
from exactly_lib_test.type_system.logic.string_model.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        from_lines.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
