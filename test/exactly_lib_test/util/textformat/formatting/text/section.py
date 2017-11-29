import unittest

from exactly_lib.util.textformat.formatting.text import lists as lf
from exactly_lib.util.textformat.formatting.text import paragraph_item
from exactly_lib.util.textformat.formatting.text import section as sut
from exactly_lib.util.textformat.structure import document
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget
from exactly_lib.util.textformat.structure.document import SectionContents, Section, Article, empty_section_contents, \
    ArticleContents, empty_article_contents
from exactly_lib_test.util.textformat.test_resources.constr import single_text_para, header_only_item, \
    BLANK_LINE, text, CROSS_REF_TITLE_ONLY_TEXT_FORMATTER


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestSectionContents))
    ret_val.addTest(unittest.makeSuite(TestSection))
    return ret_val


class TestSectionContents(unittest.TestCase):
    def test_only_initial_paragraphs(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=5),
                                                            num_item_separator_lines=1,
                                                            list_formats=lf.ListFormats(
                                                                variable_list_format=lf.ListFormat(
                                                                    lf.HeaderAndIndentFormatPlain(),
                                                                    lists.Separations(0, 0),
                                                                    indent_str='')))
        formatter = sut.Formatter(paragraph_item_formatter)
        section_contents = SectionContents([single_text_para('12345 123 5'),
                                            lists.HeaderContentList([header_only_item('12345 123')],
                                                                    lists.Format(lists.ListType.VARIABLE_LIST),
                                                                    )],
                                           [])
        actual = formatter.format_section_contents(section_contents)
        self.assertEqual(['12345',
                          '123 5',
                          BLANK_LINE,
                          '12345',
                          '123'],
                         actual)

    def test_multiple_and_nested_sub_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        section_contents = SectionContents([],
                                           [empty_section('Section 1'),
                                            sut.Section(text('Section 2'),
                                                        sut.SectionContents(
                                                            [],
                                                            [empty_article('Section 2.1')]))
                                            ])
        actual = formatter.format_section_contents(section_contents)
        self.assertEqual(['Section 1',
                          BLANK_LINE,
                          'Section 2',
                          BLANK_LINE,
                          BLANK_LINE,
                          'Section 2.1',
                          ],
                         actual)

    def test_initial_paragraph_and_single_sub_section(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        section_contents = SectionContents([single_text_para('initial paragraph')],
                                           [empty_section('Section Header')])
        actual = formatter.format_section_contents(section_contents)
        self.assertEqual(['initial paragraph',
                          BLANK_LINE,
                          BLANK_LINE,
                          BLANK_LINE,
                          'Section Header',
                          ],
                         actual)


class TestSection(unittest.TestCase):
    def test_empty_section_item(self):
        # ARRANGE #
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        header_string = 'Section Header'
        cases = [
            ('section', empty_section(header_string)),
            ('section with target', Section(text(header_string),
                                            empty_section_contents(),
                                            target=CrossReferenceTarget())),
            ('article', empty_article(header_string)),
            ('article with target', Article(text(header_string),
                                            empty_article_contents(),
                                            target=CrossReferenceTarget())),
        ]
        for test_case_name, section_item in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(section_item)
                # ASSERT #
                self.assertEqual([header_string],
                                 actual)

    def test_separation_between_header_and_content__with_initial_paragraphs(self):
        # ARRANGE #
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        header = text('Section Header')
        contents = SectionContents([single_text_para('initial paragraph')], [])
        cases = [
            ('section', Section(header, contents)),
            ('article', Article(header, ArticleContents([], contents))),
        ]
        for test_case_name, section_item in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(section_item)
                #  ASSERT #
                self.assertEqual(['Section Header',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  'initial paragraph',
                                  ],
                                 actual)

    def test_article_separation_between_header_and_content(self):
        # ARRANGE #
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        header = text('Article Header')
        cases = [
            ('single abstract para / no contents para',
             Article(header,
                     ArticleContents([single_text_para('abstract paragraph')],
                                     empty_section_contents())),
             [
                 'Article Header',
                 BLANK_LINE,
                 BLANK_LINE,
                 'abstract paragraph',
             ]),
            ('single abstract para / single contents para',
             Article(header,
                     ArticleContents([single_text_para('abstract paragraph')],
                                     single_para_contents('contents paragraph'))),
             [
                 'Article Header',
                 BLANK_LINE,
                 BLANK_LINE,
                 'abstract paragraph',
                 'contents paragraph',
             ]),
            ('single abstract para / single contents para',
             Article(header,
                     ArticleContents([single_text_para('abstract paragraph')],
                                     SectionContents([],
                                                     [empty_section('Sub Section Header')]))),
             [
                 'Article Header',
                 BLANK_LINE,
                 BLANK_LINE,
                 'abstract paragraph',
                 BLANK_LINE,
                 BLANK_LINE,
                 BLANK_LINE,
                 'Sub Section Header',
             ]),
        ]
        for test_case_name, article, expected_lines in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(article)
                #  ASSERT #
                self.assertEqual(expected_lines,
                                 actual)

    def test_separation_between_header_and_content__with_only_sub_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        header_string = 'Section Header'
        contents = SectionContents([], [empty_section('Content Section Header')])
        cases = [
            ('section', Section(text(header_string),
                                contents)),
            ('article', Article(text(header_string),
                                ArticleContents([],
                                                contents))),
        ]
        for test_case_name, section_item in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(section_item)
                #  ASSERT #
                self.assertEqual([header_string,
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  'Content Section Header',
                                  ],
                                 actual)

    def test_separation_between_header_and_content__with_both_initial_paragraphs_and_sub_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        header_string = 'Section Header'
        contents = SectionContents([single_text_para('initial paragraph')],
                                   [empty_section('Content Section Header')])
        cases = [
            ('section', Section(text(header_string),
                                contents)),
            ('article', Article(text(header_string),
                                ArticleContents([],
                                                contents))),
        ]
        for test_case_name, section_item in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(section_item)
                #  ASSERT #
                self.assertEqual([header_string,
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  'initial paragraph',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  'Content Section Header',
                                  ],
                                 actual)

    def test_section_content_indent(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        content_indent = '  '
        formatter = sut.Formatter(paragraph_item_formatter,
                                  section_content_indent_str=content_indent,
                                  separation=sut.Separation(between_sections=1,
                                                            between_header_and_content=2,
                                                            between_initial_paragraphs_and_sub_sections=3))
        header = text('Section Header')
        contents = SectionContents([single_text_para('initial paragraph')],
                                   [Section(text('Sub Section Header'),
                                            empty_section_contents())])
        cases = [
            ('section', Section(header, contents)),
            ('article', Article(header, ArticleContents([], contents))),
        ]
        for test_case_name, section_item in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(section_item)
                # ASSERT #
                self.assertEqual(['Section Header',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  content_indent + 'initial paragraph',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  content_indent + 'Sub Section Header',
                                  ],
                                 actual)

    def test_section_content_indent__for_nested_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                                            paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        content_indent = '  '
        formatter = sut.Formatter(paragraph_item_formatter,
                                  section_content_indent_str=content_indent,
                                  separation=sut.Separation(between_sections=1,
                                                            between_header_and_content=2,
                                                            between_initial_paragraphs_and_sub_sections=3))
        header = text('Section 1')
        contents = SectionContents([],
                                   [Section(
                                       text('Section 1.1'),
                                       SectionContents(
                                           [single_text_para('paragraph in section 1.1')],
                                           [Section(text('Section 1.1.1'),
                                                    SectionContents(
                                                        [single_text_para('paragraph in section 1.1.1')],
                                                        []))]))])
        cases = [
            ('section', Section(header, contents)),
            ('article', Article(header, ArticleContents([], contents))),
        ]
        for test_case_name, section_item in cases:
            with self.subTest(test_case_name):
                # ACT #
                actual = formatter.format_section_item(section_item)
                #  ASSERT #
                self.assertEqual(['Section 1',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  (1 * content_indent) + 'Section 1.1',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  (2 * content_indent) + 'paragraph in section 1.1',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  (2 * content_indent) + 'Section 1.1.1',
                                  BLANK_LINE,
                                  BLANK_LINE,
                                  (3 * content_indent) + 'paragraph in section 1.1.1',
                                  ],
                                 actual)


def single_para_contents(paragraph_text: str) -> SectionContents:
    return SectionContents([single_text_para(paragraph_text)],
                           [])


def empty_section(header: str) -> Section:
    return document.empty_section(text(header))


def empty_article(header: str) -> Article:
    return document.empty_article(text(header))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
