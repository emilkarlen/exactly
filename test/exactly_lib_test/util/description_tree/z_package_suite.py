import unittest

from exactly_lib_test.util.description_tree import rendering, tree
from exactly_lib_test.util.description_tree.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        tree.suite(),
        rendering.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
