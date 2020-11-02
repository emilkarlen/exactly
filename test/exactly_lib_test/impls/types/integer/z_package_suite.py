import unittest

from exactly_lib_test.impls.types.integer import integer_sdv


def suite() -> unittest.TestSuite:
    return integer_sdv.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
