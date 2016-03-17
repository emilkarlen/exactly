import unittest

from shellcheck_lib.util.textformat.formatting import lists as lf
from shellcheck_lib.util.textformat.formatting import paragraph_item
from shellcheck_lib.util.textformat.formatting import section as sut
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.document import SectionContents, Section, empty_contents
from shellcheck_lib_test.util.textformat.test_resources.constr import single_text_para, header_only_item, \
    BLANK_LINE, text


class TestSectionContents(unittest.TestCase):
    def test_only_initial_paragraphs(self):
        paragraph_item_formatter = paragraph_item.Formatter(
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
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
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
                                                                [empty_section('Section 2.1')]))
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
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
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
    def test_empty_section(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        section = empty_section('Section Header')
        actual = formatter.format_section(section)
        self.assertEqual(['Section Header',
                          ],
                         actual)

    def test_separation_between_header_and_content__with_initial_paragraphs(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        section = Section(text('Section Header'),
                          SectionContents([single_text_para('initial paragraph')],
                                          []))
        actual = formatter.format_section(section)
        self.assertEqual(['Section Header',
                          BLANK_LINE,
                          BLANK_LINE,
                          'initial paragraph',
                          ],
                         actual)

    def test_separation_between_header_and_content__with_only_sub_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        section = Section(text('Section Header'),
                          SectionContents([],
                                          [empty_section('Content Section Header')]))
        actual = formatter.format_section(section)
        self.assertEqual(['Section Header',
                          BLANK_LINE,
                          BLANK_LINE,
                          'Content Section Header',
                          ],
                         actual)

    def test_separation_between_header_and_content__with_both_initial_paragraphs_and_sub_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.Separation(between_sections=1,
                                                 between_header_and_content=2,
                                                 between_initial_paragraphs_and_sub_sections=3))
        section = Section(text('Section Header'),
                          SectionContents([single_text_para('initial paragraph')],
                                          [empty_section('Content Section Header')]))
        actual = formatter.format_section(section)
        self.assertEqual(['Section Header',
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
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        content_indent = '  '
        formatter = sut.Formatter(paragraph_item_formatter,
                                  section_content_indent_str=content_indent,
                                  separation=sut.Separation(between_sections=1,
                                                            between_header_and_content=2,
                                                            between_initial_paragraphs_and_sub_sections=3))
        section = Section(text('Section Header'),
                          SectionContents([single_text_para('initial paragraph')],
                                          [Section(text('Section Header'),
                                                   empty_contents())]))
        actual = formatter.format_section(section)
        self.assertEqual(['Section Header',
                          BLANK_LINE,
                          BLANK_LINE,
                          content_indent + 'initial paragraph',
                          BLANK_LINE,
                          BLANK_LINE,
                          BLANK_LINE,
                          content_indent + 'Section Header',
                          ],
                         actual)

    def test_section_content_indent__for_nested_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        content_indent = '  '
        formatter = sut.Formatter(paragraph_item_formatter,
                                  section_content_indent_str=content_indent,
                                  separation=sut.Separation(between_sections=1,
                                                            between_header_and_content=2,
                                                            between_initial_paragraphs_and_sub_sections=3))
        section = Section(text('Section 1'),
                          SectionContents(
                                  [],
                                  [Section(
                                          text('Section 1.1'),
                                          SectionContents(
                                                  [single_text_para('paragraph in section 1.1')],
                                                  [Section(text('Section 1.1.1'),
                                                           SectionContents(
                                                                   [single_text_para('paragraph in section 1.1.1')],
                                                                   []))]))]))
        actual = formatter.format_section(section)
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


def single_para_contents(paragraph_text: str):
    return SectionContents([single_text_para(paragraph_text)],
                           [])


def empty_section(header: str) -> sut.Section:
    return sut.Section(text(header),
                       sut.SectionContents([], []))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestSectionContents))
    ret_val.addTest(unittest.makeSuite(TestSection))
    return ret_val


if __name__ == '__main__':
    unittest.main()
