import unittest

from exactly_lib_test.util.textformat.formatting.html import paragraph_item, section, document, utils, entity_conversion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        entity_conversion.suite(),
        utils.suite(),
        paragraph_item.suite(),
        section.suite(),
        document.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
