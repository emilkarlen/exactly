import unittest

from exactly_lib_test.util.simple_textstruct.rendering import strings


def suite() -> unittest.TestSuite:
    return strings.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
