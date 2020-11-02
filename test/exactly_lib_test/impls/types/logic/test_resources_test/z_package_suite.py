import unittest

from exactly_lib_test.impls.types.logic.test_resources_test import integration_check


def suite() -> unittest.TestSuite:
    return integration_check.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
