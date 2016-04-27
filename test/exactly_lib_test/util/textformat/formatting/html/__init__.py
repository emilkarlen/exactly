import unittest

from exactly_lib_test.util.textformat.formatting.html import paragraph_item, section, document, utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        utils.suite(),
        paragraph_item.suite(),
        section.suite(),
        document.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
