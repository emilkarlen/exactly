import unittest
from xml.etree.ElementTree import Element

from shellcheck_lib.util.textformat.formatting.html import section as sut
from shellcheck_lib.util.textformat.formatting.html.text import TextRenderer
from shellcheck_lib.util.textformat.structure.document import SectionContents
from shellcheck_lib.util.textformat.structure.structures import para
from shellcheck_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import as_unicode_str, \
    TargetRendererTestImpl, ParaWithSingleStrTextRenderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSectionContentsEmpty),
        unittest.makeSuite(TestSectionContentsWithoutSections),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestSectionContentsEmpty(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([], [])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root />',
                         xml_string)
        self.assertIs(root,
                      ret_val)


class TestSectionContentsWithoutSections(unittest.TestCase):
    def test_single_paragraph_item(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([para('the only para')], [])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>the only para</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[-1],
                      ret_val)

    def test_multiple_paragraph_items(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([para('para 1'),
                              para('para 2')],
                             [])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        xml_string = as_unicode_str(root)
        self.assertEqual('<root>'
                         '<p>para 1</p>'
                         '<p>para 2</p>'
                         '</root>',
                         xml_string)
        self.assertIs(list(root)[-1],
                      ret_val)


TEST_RENDERER = sut.SectionRenderer(TextRenderer(TargetRendererTestImpl()),
                                    ParaWithSingleStrTextRenderer())
