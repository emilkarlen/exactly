import unittest

from exactly_lib_test.test_case.test_resources_test import error_description_assertions


def suite() -> unittest.TestSuite:
    return error_description_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
