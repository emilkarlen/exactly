import unittest
from xml.etree.ElementTree import Element

from shellcheck_lib.util.textformat.formatting.html.paragraph_item import paragraph as sut
from shellcheck_lib.util.textformat.formatting.html.text import TextRenderer
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph
from shellcheck_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import CrossReferenceTarget, \
    TargetRendererTestImpl
from shellcheck_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParagraph)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestParagraph(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root />',
                         xml_string)
        self.assertIs(root, ret_val)

    def test_single_string_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.StringText('string text')])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>string text</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_two_string_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.StringText('_1_'),
                          core.StringText('_2_')])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>_1_<br />_2_</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_cross_reference_to_id_in_same_document(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.CrossReferenceText('title',
                                                  CrossReferenceTarget('target'),
                                                  target_is_id_in_same_document=True),
                          ])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>'
                         '<a href="#target">title</a>'
                         '</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_cross_reference_to_not_id_in_same_document(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.CrossReferenceText('title',
                                                  CrossReferenceTarget('target'),
                                                  target_is_id_in_same_document=False),
                          ])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>'
                         '<a href="target">title</a>'
                         '</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_two_cross_reference(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.CrossReferenceText('title 1',
                                                  CrossReferenceTarget('target 1')),
                          core.CrossReferenceText('title 2',
                                                  CrossReferenceTarget('target 2'))])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>'
                         '<a href="#target 1">'
                         'title 1</a><br /><a href="#target 2">title 2'
                         '</a>'
                         '</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_cross_reference_and_string(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.CrossReferenceText('title',
                                                  CrossReferenceTarget('target'),
                                                  target_is_id_in_same_document=True),
                          core.StringText('string')])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>'
                         '<a href="#target">title</a><br />string'
                         '</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_anchor_with_string_as_anchored_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.AnchorText(CrossReferenceTarget('target'),
                                          core.StringText('concrete string')),
                          ])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>'
                         '<span id="target">concrete string</span>'
                         '</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_anchor_with_cross_reference_as_anchored_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([
            core.AnchorText(CrossReferenceTarget('anchor target'),
                            core.CrossReferenceText('cross ref title',
                                                    CrossReferenceTarget('cross ref target'),
                                                    target_is_id_in_same_document=True)),
        ])
        # ACT #
        ret_val = sut.render(TextRenderer(TARGET_RENDERER), root, para)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>'
                         '<span id="anchor target">'
                         '<a href="#cross ref target">cross ref title</a>'
                         '</span>'
                         '</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


TARGET_RENDERER = TargetRendererTestImpl()
