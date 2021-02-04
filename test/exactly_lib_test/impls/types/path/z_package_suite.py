import unittest

from exactly_lib_test.impls.types.path import parse_path, parse_within_parens


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_path.suite(),
        parse_within_parens.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
