import unittest

from exactly_lib_test.test_case.test_resources_test import sh_assertions


def suite() -> unittest.TestSuite:
    return sh_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
