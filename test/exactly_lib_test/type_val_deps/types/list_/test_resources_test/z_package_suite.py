import unittest

from exactly_lib_test.type_val_deps.types.list_.test_resources_test import list_assertions, list_ddv_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        list_assertions.suite(),
        list_ddv_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
