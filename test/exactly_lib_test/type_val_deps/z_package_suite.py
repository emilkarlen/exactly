import unittest

from exactly_lib_test.type_val_deps.dep_variants import z_package_suite as dep_variants
from exactly_lib_test.type_val_deps.sym_ref import z_package_suite as sym_ref
from exactly_lib_test.type_val_deps.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.type_val_deps.types import z_package_suite as types


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        sym_ref.suite(),
        dep_variants.suite(),
        types.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
