import unittest

from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import container_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import sdv_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sdv_assertions.suite(),
        container_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
