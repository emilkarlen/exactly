import unittest

from shellcheck_lib_test.util.textformat.formatting.html import paragraph, literal_layout


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        paragraph.suite(),
        literal_layout.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
