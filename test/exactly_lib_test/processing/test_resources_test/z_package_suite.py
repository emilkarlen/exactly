import unittest

from exactly_lib_test.processing.test_resources_test import result_assertions


def suite() -> unittest.TestSuite:
    return result_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
