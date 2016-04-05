import unittest
from xml.etree.ElementTree import Element

from shellcheck_lib.util.textformat.formatting.html import section as sut
from shellcheck_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from shellcheck_lib.util.textformat.formatting.html.text import TextRenderer
from shellcheck_lib.util.textformat.structure.core import StringText
from shellcheck_lib.util.textformat.structure.document import SectionContents, Section
from shellcheck_lib.util.textformat.structure.structures import para
from shellcheck_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import as_unicode_str, \
    TargetRendererTestImpl, ParaWithSingleStrTextRenderer, assert_contents_and_that_last_child_is_returned


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestHnSectionHeaderRenderer),
        unittest.makeSuite(TestSectionContentsEmpty),
        unittest.makeSuite(TestSectionContentsWithoutSections),
        unittest.makeSuite(TestSectionContentsWithSingleSection),
        unittest.makeSuite(TestSectionContentsWithMultipleSections),
        unittest.makeSuite(TestSection),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestHnSectionHeaderRenderer(unittest.TestCase):
    HN_SECTION_HEADER_RENDERER = HnSectionHeaderRenderer(TextRenderer(TargetRendererTestImpl()))

    def test_level_0(self):
        # ARRANGE #
        root = Element('root')
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(0),
                                                        root,
                                                        StringText('text'))
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h1>text</h1>'
            '</root>',
            root, ret_val, self)

    def test_highest_h_level(self):
        # ARRANGE #
        root = Element('root')
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(5),
                                                        root,
                                                        StringText('text'))
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h6>text</h6>'
            '</root>',
            root, ret_val, self)

    def test_level_greater_than_highest_h_level(self):
        # ARRANGE #
        root = Element('root')
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(6),
                                                        root,
                                                        StringText('text'))
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h6>text</h6>'
            '</root>',
            root, ret_val, self)


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
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<p>the only para</p>'
            '</root>',
            root, ret_val, self)

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
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<p>para 1</p>'
            '<p>para 2</p>'
            '</root>'
            ,
            root, ret_val, self)


class TestSectionContentsWithSingleSection(unittest.TestCase):
    def test_section_without_contents(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([],
                             [Section(StringText('section header'),
                                      SectionContents([],
                                                      []))])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h1>section header</h1>'
            '</root>'
            ,
            root, ret_val, self)

    def test_section_with_single_initial_para(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([],
                             [Section(StringText('section header'),
                                      SectionContents([para('initial para')],
                                                      []))])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h1>section header</h1>'
            '<p>initial para</p>'
            '</root>'
            ,
            root, ret_val, self)

    def test_section_with_single_sub_section(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents(
            [],
            [Section(StringText('header 1'),
                     SectionContents([],
                                     [Section(StringText('header 1/1'),
                                              SectionContents([], []))]))])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h1>header 1</h1>'
            '<h2>header 1/1</h2>'
            '</root>'
            ,
            root, ret_val, self)

    def test_single_sub_section_with_initial_paras_everywhere(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents(
            [para('para 0')],
            [Section(StringText('header 1'),
                     SectionContents([para('para 1')],
                                     [Section(StringText('header 1/1'),
                                              SectionContents([para('para 2')], []))]))])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<p>para 0</p>'
            '<h1>header 1</h1>'
            '<p>para 1</p>'
            '<h2>header 1/1</h2>'
            '<p>para 2</p>'
            '</root>'
            ,
            root, ret_val, self)


class TestSectionContentsWithMultipleSections(unittest.TestCase):
    def test(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([],
                             [Section(StringText('header 1'),
                                      SectionContents([], [])),
                              Section(StringText('header 2'),
                                      SectionContents([], [])),
                              ])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h1>header 1</h1>'
            '<h1>header 2</h1>'
            '</root>'
            ,
            root, ret_val, self)


class TestSection(unittest.TestCase):
    def test(self):
        # ARRANGE #
        root = Element('root')
        s = Section(
            StringText('header 1'),
            SectionContents(
                [para('para 1')],
                [Section(
                    StringText('header 1/1'),
                    SectionContents(
                        [para('para 1/1')], []))])
        )
        # ACT #
        ret_val = TEST_RENDERER.render_section(sut.Environment(0),
                                               root,
                                               s)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h1>header 1</h1>'
            '<p>para 1</p>'
            '<h2>header 1/1</h2>'
            '<p>para 1/1</p>'
            '</root>'
            ,
            root, ret_val, self)


TEST_RENDERER = sut.SectionRenderer(HnSectionHeaderRenderer(TextRenderer(TargetRendererTestImpl())),
                                    ParaWithSingleStrTextRenderer())
