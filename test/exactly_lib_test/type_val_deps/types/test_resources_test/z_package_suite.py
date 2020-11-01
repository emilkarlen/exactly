import unittest

from exactly_lib_test.type_val_deps.types.test_resources_test import matcher_sdv_type_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        matcher_sdv_type_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
