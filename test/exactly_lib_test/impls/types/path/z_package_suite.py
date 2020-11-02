import unittest

from exactly_lib_test.impls.types.path import parse_path


def suite() -> unittest.TestSuite:
    return parse_path.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
