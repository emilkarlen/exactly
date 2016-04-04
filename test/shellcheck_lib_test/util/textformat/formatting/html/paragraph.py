import unittest
from xml.etree.ElementTree import Element, tostring

from shellcheck_lib.util.textformat.formatting.html import paragraph as sut
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph


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
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root />',
                         xml_string)
        self.assertIs(root, ret_val)

    def test_single_string_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.StringText('string text')])
        # ACT #
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root><p>string text</p></root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_two_string_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.StringText('_1_'),
                          core.StringText('_2_')])
        # ACT #
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root><p>_1_<br />_2_</p></root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_cross_reference(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.CrossReferenceText('title',
                                                  CrossReferenceTarget('target')),
                          ])
        # ACT #
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root><p><a href="target">title</a></p></root>',
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
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root><p><a href="target 1">title 1</a><br /><a href="target 2">title 2</a></p></root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_cross_reference_and_string(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([core.CrossReferenceText('title',
                                                  CrossReferenceTarget('target')),
                          core.StringText('string')])
        # ACT #
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root><p><a href="target">title</a><br />string</p></root>',
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
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual('<root><p><a name="target">concrete string</a></p></root>',
                         xml_string)
        self.assertIs(list(root)[0],
                      ret_val)

    def test_single_anchor_with_cross_reference_as_anchored_text(self):
        # ARRANGE #
        root = Element('root')
        para = Paragraph([
            core.AnchorText(CrossReferenceTarget('anchor target'),
                            core.CrossReferenceText('cross ref title',
                                                    CrossReferenceTarget('cross ref target'))),
        ])
        # ACT #
        ret_val = sut.render(TARGET_RENDERER, root, para)
        # ASSERT #
        xml_string = to_unicode_str(root)
        self.assertEqual(
            '<root><p><a name="anchor target"><a href="cross ref target">cross ref title</a></a></p></root>',
            xml_string)
        self.assertIs(list(root)[0],
                      ret_val)


class CrossReferenceTarget(core.CrossReferenceTarget):
    def __init__(self, name: str):
        self.name = name


class TargetRenderer(sut.TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        assert isinstance(target, CrossReferenceTarget)
        return target.name


TARGET_RENDERER = TargetRenderer()


def to_unicode_str(root: Element):
    return tostring(root, encoding="unicode")
