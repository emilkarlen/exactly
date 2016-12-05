import unittest

from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat import parse as sut
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib_test.util.textformat.test_resources import parse as test_resource


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseEmpty))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraphWithSingleText))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraphWithMultipleTexts))
    ret_val.addTest(unittest.makeSuite(TestMultipleParagraphs))
    ret_val.addTest(unittest.makeSuite(TestLiteral))

    ret_val.addTest(unittest.makeSuite(TestNormalize))

    ret_val.addTest(unittest.makeSuite(TestNormalizeAndParse))
    return ret_val


class TestNormalize(unittest.TestCase):
    def test_identity(self):
        normalized_lines = ['1',
                            ''
                            '  3',
                            '4']
        actual = sut.normalize_lines(lines_content(normalized_lines))
        self.assertEqual(normalized_lines,
                         actual)

    def test_indentation(self):
        normalized_lines = ['1',
                            ''
                            '  3',
                            '4']
        indented_lines = ['  ' + line for line in normalized_lines]
        actual = sut.normalize_lines(lines_content(indented_lines))
        self.assertEqual(normalized_lines,
                         actual)

    def test_strip_empty_lines(self):
        lines = ['',
                 '   '
                 'non-empty',
                 '  ',
                 '',
                 '   ']
        indented_lines = ['  ' + line for line in lines]
        actual = sut.normalize_lines(lines_content(indented_lines))
        self.assertEqual(['non-empty'],
                         actual)


class TestParseEmpty(unittest.TestCase):
    def test_empty_input(self):
        test_resource.check(self,
                            [],
                            sut.parse([]))


class TestSingleParagraphWithSingleText(unittest.TestCase):
    def test_single_text_block_on_single_line(self):
        test_resource.check(self,
                            [Paragraph([StringText('the text block')])],
                            sut.parse(['the text block']))

    def test_single_text_block_on_multiple_lines(self):
        input_lines = ['the',
                       'text',
                       'block'
                       ]
        test_resource.check(self,
                            [Paragraph([StringText(' '.join(input_lines))])],
                            sut.parse(input_lines))

    def test_strip_text_strings(self):
        test_resource.check(self,
                            [Paragraph([StringText('the text block')])],
                            sut.parse(['  the text block   ']))


class TestSingleParagraphWithMultipleTexts(unittest.TestCase):
    def test_single_line_text_blocks(self):
        test_resource.check(self,
                            [Paragraph([StringText('text 1'),
                                        StringText('text 2')])],
                            sut.parse(['text 1'] +
                                      sut.TEXT_SEPARATOR_LINES +
                                      ['text 2']))

    def test_multi_line_text_blocks(self):
        input_lines = ['text',
                       '1'] + \
                      sut.TEXT_SEPARATOR_LINES + \
                      ['text',
                       '2']
        test_resource.check(self,
                            [Paragraph([StringText('text 1'),
                                        StringText('text 2')])],
                            sut.parse(input_lines))


class TestMultipleParagraphs(unittest.TestCase):
    def test_single_line_text_blocks(self):
        test_resource.check(self,
                            [Paragraph([StringText('text in para 1')]),
                             Paragraph([StringText('text in para 2')])],
                            sut.parse(['text in para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['text in para 2']))

    def test_multiple_text_blocks(self):
        test_resource.check(self,
                            [Paragraph([StringText('text 1 in para 1'),
                                        StringText('text 2 in para 1')]),
                             Paragraph([StringText('text 1 in para 2'),
                                        StringText('text 2 in para 2')])],
                            sut.parse(['text 1 in para 1'] +
                                      sut.TEXT_SEPARATOR_LINES +
                                      ['text 2 in para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['text 1 in para 2'] +
                                      sut.TEXT_SEPARATOR_LINES +
                                      ['text 2 in para 2']))

    def test_larger_paragraph_separator(self):
        test_resource.check(self,
                            [Paragraph([StringText('text in para 1')]),
                             Paragraph([StringText('text in para 2')])],
                            sut.parse(['text in para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['text in para 2']))


class TestLiteral(unittest.TestCase):
    def test_single_literal_block(self):
        test_resource.check(self,
                            [sut.LiteralLayout(lines_content(['literal line']))],
                            sut.parse(['```',
                                       'literal line',
                                       '```',
                                       ]))

    def test_escaping_markup_token_inside_literal_block(self):
        test_resource.check(self,
                            [sut.LiteralLayout(lines_content(['```']))],
                            sut.parse(['```',
                                       '\\```',
                                       '```',
                                       ]))

    def test_missing_closing_brace_should_raise_exception(self):
        with self.assertRaises(ValueError):
            sut.parse(['```',
                       'literal line',
                       ])

    def test_escaping_markup_token_should_make_contents_be_treated_as_normal_paragraph(self):
        test_resource.check(self,
                            [Paragraph([StringText('``` line')])],
                            sut.parse(['\\```',
                                       'line',
                                       ]))

    def test_escaping_backslash(self):
        test_resource.check(self,
                            [Paragraph([StringText('\\``` line')])],
                            sut.parse(['\\\\```',
                                       'line',
                                       ]))

    def test_literal_block_with_blank_lines_should_not_split_block(self):
        test_resource.check(self,
                            [sut.LiteralLayout(lines_content(['first line'] +
                                                             sut.PARAGRAPH_SEPARATOR_LINES +
                                                             ['last line']))],
                            sut.parse(['```',
                                       'first line'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['last line',
                                       '```',
                                       ]))

    def test_literal_block_between_paragraph_blocks(self):
        test_resource.check(self,
                            [
                                Paragraph([StringText('para 1')]),
                                sut.LiteralLayout(lines_content(['literal line'])),
                                Paragraph([StringText('para 2')]),
                            ],
                            sut.parse(['para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['```',
                                       'literal line',
                                       '```'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['para 2']))


class TestItemizedList(unittest.TestCase):
    EXPECTED_LIST_FORMAT = lists.Format(lists.ListType.ITEMIZED_LIST,
                                        custom_indent_spaces=sut.DEFAULT_LIST_SETTINGS.custom_indent_spaces,
                                        custom_separations=sut.DEFAULT_LIST_SETTINGS.custom_separations)

    def test_single_list_with_single_item(self):
        expected = [lists.HeaderContentList([_list_item('item')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['  * item'])
        test_resource.check(self, expected, actual)

    def test_single_list_with_multiple_items(self):
        expected = [lists.HeaderContentList([_list_item('item 1'),
                                             _list_item('item 2')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['  * item 1',
                            '  * item 2'])
        test_resource.check(self, expected, actual)

    def test_single_list_with_multiple_items_with_other_indentation_level(self):
        expected = [lists.HeaderContentList([_list_item('item 1'),
                                             _list_item('item 2')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['    * item 1',
                            '    * item 2'])
        test_resource.check(self, expected, actual)

    def test_single_list_with_multiple_items_separated_by_empty_line(self):
        expected = [lists.HeaderContentList([_list_item('item 1'),
                                             _list_item('item 2')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['  * item 1',
                            '',
                            '  * item 2'])
        test_resource.check(self, expected, actual)

    def test_spaces_around_header_string_SHOULD_not_appear_in_header(self):
        expected = [lists.HeaderContentList([_list_item('item 1'),
                                             _list_item('item 2')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['  *   item 1',
                            '  *  item 2   '])
        test_resource.check(self, expected, actual)

    def test_single_list_with_multiple_items_with_initial_blank_lines(self):
        expected = [lists.HeaderContentList([_list_item('item 1'),
                                             _list_item('item 2')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['',
                            '  * item 1',
                            '  * item 2'])
        test_resource.check(self, expected, actual)

    def test_single_list_with_multiple_items_with_trailing_blank_lines(self):
        expected = [lists.HeaderContentList([_list_item('item 1'),
                                             _list_item('item 2')],
                                            self.EXPECTED_LIST_FORMAT)]
        actual = sut.parse(['  * item 1',
                            '  * item 2',
                            ''])
        test_resource.check(self, expected, actual)

    def test_list_in_middle_of_paragraphs(self):
        expected = [
            Paragraph([StringText('first paragraph')]),
            lists.HeaderContentList([_list_item('item 1'),
                                     _list_item('item 2')],
                                    self.EXPECTED_LIST_FORMAT),
            Paragraph([StringText('last paragraph')]),
        ]
        actual = sut.parse(['first paragraph',
                            '',
                            '',
                            '  * item 1',
                            '  * item 2',
                            '',
                            '',
                            'last paragraph'])
        test_resource.check(self, expected, actual)


class TestNormalizeAndParse(unittest.TestCase):
    def test_misc(self):
        lines = ['',
                 '   ',
                 'para 1 text 1',
                 '  ',
                 '',
                 '   ',
                 '  para 2 text 1',
                 '  ',
                 'para 2 text 2  ',
                 '  ',
                 '\tpara 2 text 3  ',
                 '',
                 '   ']
        indented_lines = ['  ' + line for line in lines]
        actual = sut.normalize_and_parse(lines_content(indented_lines))
        test_resource.check(self,
                            [Paragraph([StringText('para 1 text 1')]),
                             Paragraph([StringText('para 2 text 1'),
                                        StringText('para 2 text 2'),
                                        StringText('para 2 text 3')])],
                            actual)


_text = StringText


def _list_item(header: str) -> lists.HeaderContentListItem:
    return lists.HeaderContentListItem(_text(header), [])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
