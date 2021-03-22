import unittest

from exactly_lib_test.impls.types.string_ import parse_string, parse_here_document, parse_rich_string


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse_string.suite(),
        parse_here_document.suite(),
        parse_rich_string.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
