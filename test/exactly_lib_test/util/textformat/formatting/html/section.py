import unittest
from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.formatting.html import section as sut
from exactly_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.formatting.html.text import TextRenderer
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.document import SectionContents, Section, Article, empty_contents
from exactly_lib.util.textformat.structure.structures import para
from exactly_lib_test.util.textformat.formatting.html.paragraph_item.test_resources import TargetRendererTestImpl, \
    ParaWithSingleStrTextRenderer
from exactly_lib_test.util.textformat.formatting.html.test_resources import as_unicode_str, \
    assert_contents_and_that_last_child_is_returned


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestHnSectionHeaderRenderer),
        unittest.makeSuite(TestSectionContentsEmpty),
        unittest.makeSuite(TestSectionContentsWithoutSections),
        unittest.makeSuite(TestSectionContentsWithSingleSection),
        unittest.makeSuite(TestSectionContentsWithMultipleSections),
        unittest.makeSuite(TestSection),
        unittest.makeSuite(TestArticle),
        unittest.makeSuite(TestSectionContentsWithSectionsAndArticles),
    ])


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


class TestSectionContentsWithSectionsAndArticles(unittest.TestCase):
    def test(self):
        # ARRANGE #
        root = Element('root')
        sc = SectionContents([],
                             [Section(StringText('section header'),
                                      SectionContents([], [])),
                              Article(StringText('article header'),
                                      [],
                                      SectionContents([], [])),
                              ])
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(2),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(
            '<root>'
            '<h3>section header</h3>'
            '<article>'
            '<header>'
            '<h1>article header</h1>'
            '</header>'
            '</article>'
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
        ret_val = TEST_RENDERER.render_section_item(sut.Environment(0),
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


class TestArticle(unittest.TestCase):
    def test_simple(self):
        cases = [
            ('empty',
             Article(StringText('header'),
                     [],
                     empty_contents()),
             '<root>'
             '<article>'
             '<header>'
             '<h1>header</h1>'
             '</header>'
             '</article>'
             '</root>'
             ),
            ('single abstract paragraph',
             Article(StringText('header'),
                     [para('abstract paragraph')],
                     empty_contents()),
             '<root>'
             '<article>'
             '<header>'
             '<h1>header</h1>'
             '<p>abstract paragraph</p>'
             '</header>'
             '</article>'
             '</root>'
             )
        ]
        for test_case_name, article, expected in cases:
            with self.subTest(test_case_name):
                root = Element('root')
                environment = sut.Environment(0)
                # ACT #
                ret_val = TEST_RENDERER.render_section_item(environment,
                                                            root,
                                                            article)
                # ASSERT #
                assert_contents_and_that_last_child_is_returned(
                    expected,
                    root, ret_val, self)

    def test_complex_structure_with_reset_of_section_level(self):
        # ARRANGE #
        s = Article(
            StringText('article header'),
            [para('para in abstract')],
            SectionContents(
                [para('initial para in contents')],
                [Section(
                    StringText('header 1/1'),
                    SectionContents(
                        [para('para 1/1')],
                        [Section(
                            StringText('header 1/1/1'),
                            SectionContents(
                                [para('para 1/1/1')],
                                []))]))])
        )
        for section_level in range(3):
            with self.subTest('section level = ' + str(section_level)):
                root = Element('root')
                environment = sut.Environment(section_level)
                # ACT #
                ret_val = TEST_RENDERER.render_section_item(environment,
                                                            root,
                                                            s)
                # ASSERT #
                assert_contents_and_that_last_child_is_returned(
                    '<root>'
                    '<article>'
                    '<header>'
                    '<h1>article header</h1>'
                    '<p>para in abstract</p>'
                    '</header>'
                    '<p>initial para in contents</p>'
                    '<h1>header 1/1</h1>'
                    '<p>para 1/1</p>'
                    '<h2>header 1/1/1</h2>'
                    '<p>para 1/1/1</p>'
                    '</article>'
                    '</root>'
                    ,
                    root, ret_val, self)


TEST_RENDERER = sut.SectionRenderer(HnSectionHeaderRenderer(TextRenderer(TargetRendererTestImpl())),
                                    ParaWithSingleStrTextRenderer())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
