import unittest

from exactly_lib_test.type_val_deps.dep_variants import dir_dependent_value
from exactly_lib_test.type_val_deps.dep_variants import resolving_deps_utils
from exactly_lib_test.type_val_deps.dep_variants import w_str_rend_sdv_visitor
from exactly_lib_test.type_val_deps.dep_variants.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        dir_dependent_value.suite(),
        resolving_deps_utils.suite(),
        w_str_rend_sdv_visitor.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
