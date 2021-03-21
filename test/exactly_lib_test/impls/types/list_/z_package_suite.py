import unittest

from exactly_lib_test.impls.types.list_ import parse_list


def suite() -> unittest.TestSuite:
    return parse_list.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
