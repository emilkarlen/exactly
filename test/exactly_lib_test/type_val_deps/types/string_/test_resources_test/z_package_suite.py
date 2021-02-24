import unittest

from exactly_lib_test.type_val_deps.types.string_.test_resources_test import ddv_assertions
from exactly_lib_test.type_val_deps.types.string_.test_resources_test import sdv_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ddv_assertions.suite(),
        sdv_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
