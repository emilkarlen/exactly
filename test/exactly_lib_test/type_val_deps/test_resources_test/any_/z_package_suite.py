import unittest

from exactly_lib_test.type_val_deps.test_resources_test.any_ import restrictions_assertions


def suite() -> unittest.TestSuite:
    return restrictions_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
