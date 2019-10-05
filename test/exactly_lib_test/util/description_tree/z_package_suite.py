import unittest

from exactly_lib_test.util.description_tree import rendering, tree


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        tree.suite(),
        rendering.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
