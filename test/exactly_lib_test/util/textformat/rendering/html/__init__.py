import unittest

from exactly_lib_test.util.textformat.rendering.html import text, paragraph_item, \
    section, document, utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        utils.suite(),
        text.suite(),
        paragraph_item.suite(),
        section.suite(),
        document.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
