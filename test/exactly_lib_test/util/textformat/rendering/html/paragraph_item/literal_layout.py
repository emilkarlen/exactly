import unittest
from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.rendering.html.paragraph_item import literal_layout as sut
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib_test.util.textformat.rendering.html.test_resources import as_unicode_str


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestLiteralLayout)


class TestLiteralLayout(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        root = Element('root')
        ll = LiteralLayout(LITERAL_MULTI_LINE_TEXT)
        # ACT #
        ret_val = sut.render(root, ll)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual(LITERAL_MULTI_LINE_TEXT_RESULT,
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


LITERAL_MULTI_LINE_TEXT = """\
first line

second line
"""

LITERAL_MULTI_LINE_TEXT_RESULT = """\
<root><pre>first line

second line
</pre></root>"""

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
