import unittest

from shellcheck_lib.general.textformat.formatting import lists as lf
from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.formatting import section as sut
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.document import SectionContents
from shellcheck_lib_test.general.textformat.formatting.test_resources import single_text_para, header_only_item, \
    BLANK_LINE


class TestSectionContents(unittest.TestCase):
    def test_initial_paragraphs(self):
        paragraph_item_formatter = paragraph_item.Formatter(page_width=100,
                                                            num_item_separator_lines=1,
                                                            list_formats=lf.ListFormats(
                                                                variable_list_format=lf.ListFormat(
                                                                    lf.HeaderAndIndentFormatPlain(),
                                                                    lf.Separations(0, 0))))
        formatter = sut.Formatter(paragraph_item_formatter)
        section_contents = SectionContents([single_text_para('paragraph'),
                                            lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                                                  [header_only_item(
                                                                      'list item header')])],
                                           [])
        actual = formatter.format_section_contents(section_contents)
        self.assertEqual(['paragraph',
                          BLANK_LINE,
                          'list item header'],
                         actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestSectionContents))
    return ret_val


if __name__ == '__main__':
    unittest.main()
