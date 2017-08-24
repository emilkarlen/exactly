import unittest

from exactly_lib_test.named_element.test_resources_test import resolver_structure_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        resolver_structure_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
