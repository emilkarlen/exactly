import unittest

from exactly_lib_test.impls.types.line_matcher.contents import parse, string_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        string_source.suite(),
        parse.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
