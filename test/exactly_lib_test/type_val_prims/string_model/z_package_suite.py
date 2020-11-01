import unittest

from exactly_lib_test.type_val_prims.string_model import from_lines, string_model
from exactly_lib_test.type_val_prims.string_model.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        string_model.suite(),
        from_lines.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
