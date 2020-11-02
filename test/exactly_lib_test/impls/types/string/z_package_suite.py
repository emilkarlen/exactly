import unittest

from exactly_lib_test.impls.types.string import parse_string, parse_here_document


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_string.suite(),
        parse_here_document.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
