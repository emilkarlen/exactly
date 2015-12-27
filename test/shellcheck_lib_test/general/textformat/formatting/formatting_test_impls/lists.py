import unittest

from shellcheck_lib.general.textformat.formatting import lists as lf
from shellcheck_lib.general.textformat.formatting import paragraph_item as sut
from shellcheck_lib.general.textformat.structure import core
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib_test.general.textformat.test_resources.constr import single_text_para, item, header_only_item, \
    BLANK_LINE

NO_SEPARATIONS = lf.Separations(num_blank_lines_between_elements=0,
                                num_blank_lines_between_header_and_contents=0)

list_formatter_with_no_blank_lines = lf.ListFormat(lf.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=3),
                                                   NO_SEPARATIONS)


class TestHeaderOnlyListItemsWithNoLineWraps(unittest.TestCase):
    def test_empty_list(self):
        items = []
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_formatter_with_no_blank_lines)
        self.assertEqual([],
                         actual)

    def test_singleton_list(self):
        items = [header_only_item('header')]
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_formatter_with_no_blank_lines)
        self.assertEqual(['1. header'],
                         actual)

    def test_multi_element_list(self):
        items = [header_only_item('header 1'),
                 header_only_item('header 2')]
        formatter = formatter_with_page_width(20)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_formatter_with_no_blank_lines)
        self.assertEqual(['1. header 1',
                          '2. header 2'],
                         actual)


class TestHeaderOnlyListItemsWithLineWraps(unittest.TestCase):
    def test_singleton_list(self):
        formatter = formatter_with_page_width(5)
        items = [header_only_item('45 4')]
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_formatter_with_no_blank_lines)
        self.assertEqual(['1. 45',
                          '   4'],
                         actual)

    def test_multi_element_list(self):
        formatter = formatter_with_page_width(5)
        items = [header_only_item('45 4'),
                 header_only_item('ab c')]
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_formatter_with_no_blank_lines)
        self.assertEqual(['1. 45',
                          '   4',
                          '2. ab',
                          '   c'],
                         actual)

    def test_varying_header_following_line_indent(self):
        formatter = formatter_with_page_width(4)
        items = [header_only_item('h1 X'),
                 header_only_item('h2 Y'),
                 header_only_item('h3 Z')]
        list_format = lf.ListFormat(HeaderFormatWithVaryingFollowingLineIndent(3),
                                    NO_SEPARATIONS)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_format)
        self.assertEqual(['**h1',
                          '  X',
                          '*h2',
                          ' Y',
                          '**h3',
                          '  Z'],
                         actual)


class TestThatIdentationIsNotModified(unittest.TestCase):
    def test_without_content(self):
        formatter = formatter_with_page_width(4)
        current_indent_before = formatter.wrapper.current_indent
        indent_stack_before = formatter.wrapper.saved_indents_stack.copy()
        items = [header_only_item('h1 X'),
                 header_only_item('h2 Y')]
        list_format = lf.ListFormat(HeaderFormatWithVaryingFollowingLineIndent(3),
                                    NO_SEPARATIONS)
        formatter.format_header_value_list_according_to_format(items,
                                                               list_format)
        self.assertEqual(current_indent_before,
                         formatter.wrapper.current_indent,
                         'Current indent')

        self.assertEqual(indent_stack_before,
                         formatter.wrapper.saved_indents_stack,
                         'Saved indents stack')

    def test_with_content(self):
        list_format = lf.ListFormat(lf.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=1),
                                    NO_SEPARATIONS)
        items = [item('header',
                      [single_text_para('2345678')])]
        formatter = formatter_with_page_width(10)
        current_indent_before = formatter.wrapper.current_indent
        indent_stack_before = formatter.wrapper.saved_indents_stack.copy()
        formatter.format_header_value_list_according_to_format(items,
                                                               list_format)
        self.assertEqual(current_indent_before,
                         formatter.wrapper.current_indent,
                         'Current indent')

        self.assertEqual(indent_stack_before,
                         formatter.wrapper.saved_indents_stack,
                         'Saved indents stack')


class TestContentFormatting(unittest.TestCase):
    def test_singleton_list(self):
        list_format = lf.ListFormat(lf.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=1),
                                    NO_SEPARATIONS)
        items = [item('header',
                      [single_text_para('2345678 abc def')])]
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_format)
        self.assertEqual(['1. header',
                          ' 2345678',
                          ' abc def'],
                         actual)

    def test_multi_element_list(self):
        list_format = lf.ListFormat(lf.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=1),
                                    NO_SEPARATIONS)
        items = [item('h1',
                      [single_text_para('2345678')]),
                 item('h2',
                      [single_text_para('content 1'),
                       single_text_para('content 2')])]
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_format)
        self.assertEqual(['1. h1',
                          ' 2345678',
                          '2. h2',
                          ' content 1',
                          BLANK_LINE,
                          ' content 2'],
                         actual)


class TestWholeListIndent(unittest.TestCase):
    def test_with_given_indent(self):
        indent_str = '[INDENT]'
        list_format = lf.ListFormat(lf.HeaderAndIndentFormatPlain(contents_indent_spaces=4),
                                    NO_SEPARATIONS,
                                    indent_str=indent_str)
        items = [item('header',
                      [single_text_para('contents')])]
        formatter = formatter_with_page_width(100)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        list_format)
        self.assertEqual([indent_str + 'header',
                          indent_str + (4 * ' ') + 'contents'],
                         actual)

    def test_with_resolved_indent(self):
        format_indent_spaces = 2
        indent_str = format_indent_spaces * ' '
        list_format = lf.ListFormat(lf.HeaderAndIndentFormatPlain(contents_indent_spaces=4),
                                    NO_SEPARATIONS,
                                    indent_str=indent_str)
        items = [item('header',
                      [single_text_para('contents')])]
        the_list = sut.HeaderContentList(lists.ListType.VARIABLE_LIST,
                                         items)
        formatter = sut.Formatter(sut.Wrapper(page_width=100),
                                  list_formats=lf.ListFormats(variable_list_format=list_format))
        actual = formatter.format_header_content_list(the_list)
        self.assertEqual([indent_str + 'header',
                          indent_str + (4 * ' ') + 'contents'],
                         actual)

    def test_with_custom_indent(self):
        custom_indent_spaces = 5
        custom_indent_str = custom_indent_spaces * ' '
        content_indent_spaces = 4
        content_indent_str = content_indent_spaces * ' '
        list_format = lf.ListFormat(lf.HeaderAndIndentFormatPlain(contents_indent_spaces=content_indent_spaces),
                                    NO_SEPARATIONS,
                                    indent_str='should not be used since overridden by custom indent')
        items = [item('header',
                      [single_text_para('contents')])]
        the_list = sut.HeaderContentList(lists.ListType.VARIABLE_LIST,
                                         items,
                                         custom_indent_spaces=custom_indent_spaces)
        formatter = sut.Formatter(sut.Wrapper(page_width=100),
                                  list_formats=lf.ListFormats(variable_list_format=list_format))
        actual = formatter.format_header_content_list(the_list)
        self.assertEqual([custom_indent_str + 'header',
                          custom_indent_str + content_indent_str + 'contents'],
                         actual)


class TestSeparations(unittest.TestCase):
    list_format = lf.ListFormat(lf.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=1),
                                lf.Separations(num_blank_lines_between_elements=2,
                                               num_blank_lines_between_header_and_contents=1))

    def test_empty_list(self):
        items = []
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        self.list_format)
        self.assertEqual([],
                         actual)

    def test_singleton_list(self):
        items = [header_only_item('header')]
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        self.list_format)
        self.assertEqual(['1. header'],
                         actual)

    def test_multi_element_list__no_content(self):
        items = [header_only_item('header 1'),
                 header_only_item('header 2')]
        formatter = formatter_with_page_width(20)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        self.list_format)
        self.assertEqual(['1. header 1',
                          BLANK_LINE,
                          BLANK_LINE,
                          '2. header 2'],
                         actual)

    def test_item_with_content(self):
        items = [item('header',
                      [single_text_para('content')])]
        formatter = formatter_with_page_width(10)
        actual = formatter.format_header_value_list_according_to_format(items,
                                                                        self.list_format)
        self.assertEqual(['1. header',
                          BLANK_LINE,
                          ' content'],
                         actual)


class TestResolveListFormat(unittest.TestCase):
    LIST_FORMATS = lf.ListFormats(itemized_list_format=lf.ListFormat(lf.HeaderAndIndentFormatWithMarker('*'),
                                                                     NO_SEPARATIONS),
                                  ordered_list_format=lf.ListFormat(lf.HeaderAndIndentFormatWithNumbering(),
                                                                    NO_SEPARATIONS),
                                  variable_list_format=lf.ListFormat(lf.HeaderAndIndentFormatPlain(),
                                                                     NO_SEPARATIONS))

    def test_itemized_list(self):
        items = [header_only_item('header')]
        formatter = sut.Formatter(sut.Wrapper(page_width=100),
                                  list_formats=self.LIST_FORMATS)
        actual = formatter.format_header_content_list(lists.HeaderContentList(lists.ListType.ITEMIZED_LIST,
                                                                              items))
        self.assertEqual(['* header'],
                         actual)

    def test_ordered_list(self):
        items = [header_only_item('header')]
        formatter = sut.Formatter(sut.Wrapper(page_width=100),
                                  list_formats=self.LIST_FORMATS)
        actual = formatter.format_header_content_list(lists.HeaderContentList(lists.ListType.ORDERED_LIST,
                                                                              items))
        self.assertEqual(['1. header'],
                         actual)

    def test_variable_list(self):
        items = [header_only_item('header')]
        formatter = sut.Formatter(sut.Wrapper(page_width=100),
                                  list_formats=self.LIST_FORMATS)
        actual = formatter.format_header_content_list(lists.HeaderContentList(lists.ListType.VARIABLE_LIST,
                                                                              items))
        self.assertEqual(['header'],
                         actual)


class HeaderFormatWithVaryingFollowingLineIndent(lf.HeaderAndIndentFormatWithConstantValueIndentBase):
    def __init__(self, contents_indent_spaces: int):
        super().__init__(contents_indent_spaces)

    def header_text(self,
                    element_number: int,
                    total_number_of_elements: int,
                    header: core.Text) -> core.Text:
        return core.Text(self._prefix(element_number) + header.value)

    def following_header_lines_indent(self,
                                      element_number: int,
                                      total_number_of_elements: int) -> str:
        return len(self._prefix(element_number)) * ' '

    @staticmethod
    def _prefix(element_number: int) -> str:
        return '*' if element_number % 2 == 0 else '**'


def formatter_with_page_width(page_width: int) -> sut.Formatter:
    return sut.Formatter(sut.Wrapper(page_width=page_width))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestHeaderOnlyListItemsWithNoLineWraps))
    ret_val.addTest(unittest.makeSuite(TestHeaderOnlyListItemsWithLineWraps))
    ret_val.addTest(unittest.makeSuite(TestContentFormatting))
    ret_val.addTest(unittest.makeSuite(TestThatIdentationIsNotModified))
    ret_val.addTest(unittest.makeSuite(TestResolveListFormat))
    ret_val.addTest(unittest.makeSuite(TestWholeListIndent))
    return ret_val


if __name__ == '__main__':
    unittest.main()
