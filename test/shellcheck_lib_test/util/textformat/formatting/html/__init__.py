import unittest

from shellcheck_lib_test.util.textformat.formatting.html import paragraph, literal_layout, lists


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        literal_layout.suite(),
        paragraph.suite(),
        lists.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
