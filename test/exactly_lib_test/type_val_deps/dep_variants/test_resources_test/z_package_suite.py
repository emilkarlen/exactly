import unittest

from exactly_lib_test.type_val_deps.dep_variants.test_resources_test import dir_dependent_value, \
    dir_dep_value_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        dir_dependent_value.suite(),
        dir_dep_value_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
