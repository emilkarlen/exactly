import unittest

from exactly_lib_test.type_val_deps.types.path import concrete_path_parts, path_description, paths
from exactly_lib_test.type_val_deps.types.path.path_sdv_impls import z_package_suite as path_sdv_impls
from exactly_lib_test.type_val_deps.types.path.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        path_description.suite(),
        concrete_path_parts.suite(),
        paths.suite(),
        path_sdv_impls.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
