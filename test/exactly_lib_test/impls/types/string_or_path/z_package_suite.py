import unittest

from exactly_lib_test.impls.types.string_or_path import parse_string_or_path


def suite() -> unittest.TestSuite:
    return parse_string_or_path.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
