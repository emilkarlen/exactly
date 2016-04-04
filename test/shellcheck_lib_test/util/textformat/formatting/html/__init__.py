import unittest

from shellcheck_lib_test.util.textformat.formatting.html import paragraph_item


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        paragraph_item.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
