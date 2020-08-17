import unittest
from xml.etree.ElementTree import Element

from exactly_lib.util.textformat.rendering.html import section as sut
from exactly_lib.util.textformat.rendering.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.rendering.html.text import TextRenderer
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.document import SectionContents, Section, Article, empty_section_contents, \
    ArticleContents
from exactly_lib.util.textformat.structure.structures import para
from exactly_lib_test.test_resources.xml_etree import element
from exactly_lib_test.util.textformat.rendering.html.paragraph_item.test_resources import ParaWithSingleStrTextRenderer
from exactly_lib_test.util.textformat.rendering.html.test_resources import as_unicode_str, \
    CrossReferenceTargetTestImpl, \
    TARGET_RENDERER_AS_NAME, assert_contents_and_that_last_child_is_returned


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
    HN_SECTION_HEADER_RENDERER = HnSectionHeaderRenderer(TextRenderer(TARGET_RENDERER_AS_NAME))

    def test_level_0(self):
        # ARRANGE #
        root = Element('root')
        header_text = 'text'

        expected_element = element(
            root.tag,
            children=[
                element('h1', text=header_text)
            ]
        )
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(0),
                                                        root,
                                                        StringText(header_text),
                                                        {})
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root, ret_val, self)

    def test_with_attributes(self):
        # ARRANGE #
        root_to_mutate = Element('root')
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(3),
                                                        root_to_mutate,
                                                        StringText('text'),
                                                        {'attr1': 'attr1-value',
                                                         'attr2': 'attr2-value'})
        expected_element = element(
            root_to_mutate.tag,
            children=[
                element('h4',
                        attributes={'attr1': 'attr1-value',
                                    'attr2': 'attr2-value'},
                        text='text'
                        )
            ]

        )
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_to_mutate, ret_val, self)

    def test_highest_h_level(self):
        # ARRANGE #
        root = Element('root')
        header_text = 'text'

        expected_element = element(
            root.tag,
            children=[
                element('h6', text=header_text)
            ]
        )
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(5),
                                                        root,
                                                        StringText(header_text),
                                                        {})
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root, ret_val, self)

    def test_level_greater_than_highest_h_level(self):
        # ARRANGE #
        root = Element('root')
        header_text = 'text'
        expected_element = element(
            root.tag,
            children=[
                element('h6', text=header_text)
            ]
        )
        # ACT #
        ret_val = self.HN_SECTION_HEADER_RENDERER.apply(sut.Environment(6),
                                                        root,
                                                        StringText(header_text),
                                                        {})
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root, ret_val, self)


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
        paragraph_text = 'the only para'
        sc = SectionContents([para(paragraph_text)], [])

        expected_element = element(
            root.tag,
            children=[
                element('p', text=paragraph_text)
            ]
        )

        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root, ret_val, self)

    def test_multiple_paragraph_items(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        paragraph_1_text = 'para 1'
        paragraph_2_text = 'para 2'
        sc = SectionContents([para(paragraph_1_text),
                              para(paragraph_2_text)],
                             [])

        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('p', text=paragraph_1_text),
                element('p', text=paragraph_2_text),
            ]
        )

        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)


class TestSectionContentsWithSingleSection(unittest.TestCase):
    def test_section_without_contents(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        section_header_text = 'section header'
        sc = SectionContents([],
                             [Section(StringText(section_header_text),
                                      SectionContents([],
                                                      []))])

        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('section',
                        children=[
                            _header_w_h(section_header_text),
                        ])
            ]
        )
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)

    def test_section_with_single_initial_para(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        section_header_text = 'section header'
        initial_para_text = 'initial para'
        sc = SectionContents([],
                             [Section(StringText(section_header_text),
                                      SectionContents([para(initial_para_text)],
                                                      []))])
        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('section',
                        children=[
                            _header_w_h(section_header_text),
                            element('p', text=initial_para_text)
                        ])
            ]
        )
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)

    def test_section_with_single_sub_section(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        header_1_text = 'header 1'
        header_1_1_text = 'header 1/1'
        sc = SectionContents(
            [],
            [Section(StringText(header_1_text),
                     SectionContents([],
                                     [Section(StringText(header_1_1_text),
                                              SectionContents([], []))]))]
        )
        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('section',
                        children=[
                            _header_w_h(header_1_text),
                            element('section',
                                    children=[
                                        _header_w_h(header_1_1_text, 'h2'),
                                    ]),
                        ]),
            ]
        )
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)

    def test_single_sub_section_with_initial_paras_everywhere(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        para_0_text = 'para 0'
        header_1_text = 'header 1'
        para_1_text = 'para 1'
        header_1_1_text = 'header 1/1'
        para_2_text = 'para 2'
        sc = SectionContents(
            [para(para_0_text)],
            [Section(StringText(header_1_text),
                     SectionContents([para(para_1_text)],
                                     [Section(StringText(header_1_1_text),
                                              SectionContents([para(para_2_text)], []))]))]
        )
        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('p', text=para_0_text),
                element('section',
                        children=[
                            _header_w_h(header_1_text),
                            element('p', text=para_1_text),
                            element('section',
                                    children=[
                                        _header_w_h(header_1_1_text, 'h2'),
                                        element('p', text=para_2_text),
                                    ])
                        ]),
            ]
        )

        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)


class TestSectionContentsWithMultipleSections(unittest.TestCase):
    def test(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        header_1_text = 'header 1'
        header_2_text = 'header 2'
        sc = SectionContents(
            [],
            [Section(StringText(header_1_text),
                     SectionContents([], [])),
             Section(StringText(header_2_text),
                     SectionContents([], [])),
             ]
        )
        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('section',
                        children=[
                            _header_w_h(header_1_text),
                        ]),
                element('section',
                        children=[
                            _header_w_h(header_2_text),
                        ]),
            ]
        )
        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(0),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)


class TestSectionContentsWithSectionsAndArticles(unittest.TestCase):
    def test(self):
        # ARRANGE #
        root_element_to_mutate = Element('root')
        section_header_text = 'section header'
        article_header_text = 'article header'
        sc = SectionContents([],
                             [Section(StringText(section_header_text),
                                      SectionContents([], [])),
                              Article(StringText(article_header_text),
                                      ArticleContents([],
                                                      SectionContents([], []))),
                              ]
                             )
        expected_element = element(
            root_element_to_mutate.tag,
            children=[
                element('section',
                        children=[
                            _header_w_h(section_header_text, 'h3'),
                        ]),
                element('article',
                        children=[
                            _header_w_h(article_header_text),
                        ]),
            ]
        )

        # ACT #
        ret_val = TEST_RENDERER.render_section_contents(sut.Environment(2),
                                                        root_element_to_mutate,
                                                        sc)
        # ASSERT #
        assert_contents_and_that_last_child_is_returned(expected_element, root_element_to_mutate, ret_val, self)


def _header_w_h(h_text: str,
                h: str = 'h1') -> Element:
    return element(
        'header',
        children=[
            element(h, text=h_text)
        ]
    )


class TestSection(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            ('empty',
             Section(
                 StringText('header 1'),
                 empty_section_contents()),
             element(
                 'root',
                 children=[
                     element(
                         'section',
                         children=[
                             _header_w_h('header 1'),
                         ])
                 ])
             ),
            ('empty with target',
             Section(
                 StringText('header 1'),
                 empty_section_contents(),
                 target=CrossReferenceTargetTestImpl('section-target-name')),
             element(
                 'root',
                 children=[
                     element(
                         'section',
                         attributes={'id': 'section-target-name'},
                         children=[_header_w_h('header 1')]
                     )
                 ]
             )
             ),
            ('empty with tags',
             Section(
                 StringText('header 1'),
                 empty_section_contents(),
                 tags={'first-label', 'second-label'}),
             element(
                 'root',
                 children=[
                     element(
                         'section',
                         attributes={'class': 'first-label second-label'},
                         children=[_header_w_h('header 1')]
                     )
                 ])
             ),
            ('empty with target and tags',
             Section(
                 StringText('header 1'),
                 empty_section_contents(),
                 target=CrossReferenceTargetTestImpl('t'),
                 tags={'l1', 'l2'}),
             element(
                 'root',
                 children=[
                     element(
                         'section',
                         attributes={'class': 'l1 l2',
                                     'id': 't'},
                         children=[_header_w_h('header 1')]
                     )
                 ])
             ),
            ('with contents',
             Section(
                 StringText('header 1'),
                 SectionContents(
                     [para('para 1')],
                     [Section(
                         StringText('header 1/1'),
                         SectionContents(
                             [para('para 1/1')], []))])
             ),
             element(
                 'root',
                 children=[
                     element(
                         'section',
                         children=[
                             _header_w_h('header 1'),
                             element('p', text='para 1'),
                             element(
                                 'section',
                                 children=[
                                     _header_w_h('header 1/1', 'h2'),
                                     element('p', text='para 1/1'),
                                 ]
                             )
                         ]
                     )
                 ]
             )
             ),
        ]
        for test_case_name, section, expected in cases:
            with self.subTest(test_case_name):
                root_element_to_mutate = Element('root')
                # ACT #
                ret_val = TEST_RENDERER.render_section_item(sut.Environment(0),
                                                            root_element_to_mutate,
                                                            section)
                # ASSERT #
                assert_contents_and_that_last_child_is_returned(expected, root_element_to_mutate, ret_val, self)


class TestArticle(unittest.TestCase):
    def test_simple(self):
        cases = [
            ('empty',
             Article(StringText('header'),
                     ArticleContents([],
                                     empty_section_contents())),
             element(
                 'root',
                 children=[
                     element(
                         'article',
                         children=[
                             _header_w_h('header'),
                         ])
                 ])
             ),
            ('empty with target',
             Article(StringText('header'),
                     ArticleContents([],
                                     empty_section_contents()),
                     target=CrossReferenceTargetTestImpl('target-name')),
             element(
                 'root',
                 children=[
                     element(
                         'article',
                         attributes={'id': 'target-name'},
                         children=[_header_w_h('header')]
                     )
                 ]
             )
             ),
            ('empty with tags',
             Article(StringText('header'),
                     ArticleContents([],
                                     empty_section_contents()),
                     tags={'label1', 'label2'}),
             element(
                 'root',
                 children=[
                     element(
                         'article',
                         attributes={'class': 'label1 label2'},
                         children=[_header_w_h('header')]
                     )
                 ])
             ),
            ('empty with target and tags',
             Article(StringText('header'),
                     ArticleContents([],
                                     empty_section_contents()),
                     target=CrossReferenceTargetTestImpl('article-target'),
                     tags={'label1', 'label2'}),
             element(
                 'root',
                 children=[
                     element(
                         'article',
                         attributes={'class': 'label1 label2',
                                     'id': 'article-target'},
                         children=[_header_w_h('header')]
                     )
                 ])
             ),
            ('single abstract paragraph',
             Article(StringText('header'),
                     ArticleContents([para('abstract paragraph')],
                                     empty_section_contents())),
             element(
                 'root',
                 children=[
                     element(
                         'article',
                         children=[
                             element(
                                 'header',
                                 children=[
                                     element('h1', text='header'),
                                     element('p', text='abstract paragraph'),
                                 ],
                             )
                         ]
                     )
                 ])
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
            ArticleContents([para('para in abstract')],
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
                                                []))]))])))
        for section_level in range(3):
            with self.subTest('section level = ' + str(section_level)):
                root = Element('root')
                environment = sut.Environment(section_level)
                # ACT #
                ret_val = TEST_RENDERER.render_section_item(environment,
                                                            root,
                                                            s)
                # ASSERT #
                expected_element = element(
                    'root',
                    children=[
                        element(
                            'article',
                            children=[
                                element(
                                    'header',
                                    children=[
                                        element('h1', text='article header'),
                                        element('p', text='para in abstract'),
                                    ],
                                ),
                                element('p', text='initial para in contents'),
                                element('section',
                                        children=[
                                            _header_w_h('header 1/1'),
                                            element('p', text='para 1/1'),
                                            element('section',
                                                    children=[
                                                        _header_w_h('header 1/1/1', 'h2'),
                                                        element('p', text='para 1/1/1'),
                                                    ])

                                        ])
                            ]
                        )
                    ])

                assert_contents_and_that_last_child_is_returned(expected_element, root, ret_val, self)


TEST_RENDERER = sut.SectionItemRenderer(TARGET_RENDERER_AS_NAME,
                                        HnSectionHeaderRenderer(TextRenderer(TARGET_RENDERER_AS_NAME)),
                                        ParaWithSingleStrTextRenderer())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
