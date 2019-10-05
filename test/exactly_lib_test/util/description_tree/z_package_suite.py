import unittest

from exactly_lib_test.util.description_tree import simple_textstruct_rendering, tree, renderers
from exactly_lib_test.util.description_tree.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        tree.suite(),
        simple_textstruct_rendering.suite(),
        renderers.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
