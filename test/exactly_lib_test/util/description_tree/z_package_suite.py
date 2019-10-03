import unittest

from exactly_lib_test.util.description_tree import rendering


def suite() -> unittest.TestSuite:
    return rendering.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
