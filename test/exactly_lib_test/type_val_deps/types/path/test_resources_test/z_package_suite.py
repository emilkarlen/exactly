import unittest

from exactly_lib_test.type_val_deps.types.path.test_resources_test import path_assertions, path_part_assertions
from exactly_lib_test.type_val_deps.types.path.test_resources_test import path_relativity
from exactly_lib_test.type_val_deps.types.path.test_resources_test import sdv_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        path_relativity.suite(),
        path_part_assertions.suite(),
        path_assertions.suite(),
        sdv_assertions.suite()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
