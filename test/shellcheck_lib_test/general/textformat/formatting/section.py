import unittest

from shellcheck_lib.general.textformat.formatting import lists as lf
from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.formatting import section as sut
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.document import SectionContents
from shellcheck_lib_test.general.textformat.formatting.test_resources import single_text_para, header_only_item, \
    BLANK_LINE, text


class TestSectionContents(unittest.TestCase):
    def test_only_initial_paragraphs(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=5),
                                                            num_item_separator_lines=1,
                                                            list_formats=lf.ListFormats(
                                                                variable_list_format=lf.ListFormat(
                                                                    lf.HeaderAndIndentFormatPlain(),
                                                                    lf.Separations(0, 0))))
        formatter = sut.Formatter(paragraph_item_formatter)
        section_contents = SectionContents([single_text_para('12345 123 5'),
                                            lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                                                  [header_only_item(
                                                                      '12345 123')])],
                                           [])
        actual = formatter.format_section_contents(section_contents)
        self.assertEqual(['12345',
                          '123 5',
                          BLANK_LINE,
                          '12345',
                          '123'],
                         actual)

    def test_sub_sections(self):
        paragraph_item_formatter = paragraph_item.Formatter(paragraph_item.Wrapper(page_width=100),
                                                            num_item_separator_lines=0)
        formatter = sut.Formatter(paragraph_item_formatter,
                                  sut.no_separation())
        section_contents = SectionContents([],
                                           [empty_section('Section 1'),
                                            sut.Section(text('Section 2'),
                                                        sut.SectionContents(
                                                            [],
                                                            [empty_section('Section 2.1')]))])
        actual = formatter.format_section_contents(section_contents)
        self.assertEqual(['Section 1',
                          'Section 2',
                          'Section 2.1',
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
    return ret_val


if __name__ == '__main__':
    unittest.main()
