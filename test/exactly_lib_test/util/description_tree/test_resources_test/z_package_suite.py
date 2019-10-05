import unittest

from exactly_lib_test.util.description_tree.test_resources_test import described_tree_assertions


def suite() -> unittest.TestSuite:
    return described_tree_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
