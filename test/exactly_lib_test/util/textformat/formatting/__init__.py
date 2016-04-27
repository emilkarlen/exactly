import unittest

from exactly_lib_test.util.textformat.formatting import text, html


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        text.suite(),
        html.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
