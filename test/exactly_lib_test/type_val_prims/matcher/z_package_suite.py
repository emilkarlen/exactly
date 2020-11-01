import unittest

from exactly_lib_test.type_val_prims.matcher import matcher_base_class


def suite() -> unittest.TestSuite:
    return matcher_base_class.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
