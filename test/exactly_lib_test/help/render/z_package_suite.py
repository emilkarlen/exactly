import unittest

from exactly_lib_test.help.render import cross_reference


def suite() -> unittest.TestSuite:
    return cross_reference.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
