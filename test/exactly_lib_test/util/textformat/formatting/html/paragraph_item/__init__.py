import unittest

from exactly_lib_test.util.textformat.formatting.html.paragraph_item import paragraph, literal_layout, lists, table


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        literal_layout.suite(),
        paragraph.suite(),
        lists.suite(),
        table.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
