import unittest

from exactly_lib_test.section_document.test_resources_test import assertions


def suite() -> unittest.TestSuite:
    return assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
