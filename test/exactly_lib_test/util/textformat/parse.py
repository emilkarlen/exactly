import unittest

from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat import parse as sut
from exactly_lib_test.util.textformat.test_resources import parse as test_resource


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
                            [sut.Paragraph([sut.StringText('the text block')])],
                            sut.parse(['the text block']))

    def test_single_text_block_on_multiple_lines(self):
        input_lines = ['the',
                       'text',
                       'block'
                       ]
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText(' '.join(input_lines))])],
                            sut.parse(input_lines))

    def test_strip_text_strings(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('the text block')])],
                            sut.parse(['  the text block   ']))


class TestSingleParagraphWithMultipleTexts(unittest.TestCase):
    def test_single_line_text_blocks(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('text 1'),
                                            sut.StringText('text 2')])],
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
                            [sut.Paragraph([sut.StringText('text 1'),
                                            sut.StringText('text 2')])],
                            sut.parse(input_lines))


class TestMultipleParagraphs(unittest.TestCase):
    def test_single_line_text_blocks(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('text in para 1')]),
                             sut.Paragraph([sut.StringText('text in para 2')])],
                            sut.parse(['text in para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['text in para 2']))

    def test_single_multiple_text_blocks(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('text 1 in para 1'),
                                            sut.StringText('text 2 in para 1')]),
                             sut.Paragraph([sut.StringText('text 1 in para 2'),
                                            sut.StringText('text 2 in para 2')])],
                            sut.parse(['text 1 in para 1'] +
                                      sut.TEXT_SEPARATOR_LINES +
                                      ['text 2 in para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['text 1 in para 2'] +
                                      sut.TEXT_SEPARATOR_LINES +
                                      ['text 2 in para 2']))


class TestMultipleParagraphsWithAlternateSeparator(unittest.TestCase):
    def test_larger_paragraph_separator(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('text in para 1')]),
                             sut.Paragraph([sut.StringText('text in para 2')])],
                            sut.parse(['text in para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['text in para 2']))


class TestLiteral(unittest.TestCase):
    def test_single_literal_block(self):
        test_resource.check(self,
                            [sut.LiteralLayout(lines_content(['literal line']))],
                            sut.parse(['@literal{',
                                       'literal line',
                                       '@}',
                                       ]))

    def test_escaping_markup_token_inside_literal_block(self):
        test_resource.check(self,
                            [sut.LiteralLayout(lines_content(['@}']))],
                            sut.parse(['@literal{',
                                       '\\@}',
                                       '@}',
                                       ]))

    def test_missing_closing_brace_should_raise_exception(self):
        with self.assertRaises(ValueError):
            sut.parse(['@literal{',
                       'literal line',
                       ])

    def test_invalid_markup_token_should_raise_exception(self):
        with self.assertRaises(ValueError):
            sut.parse(['@literal{',
                       '@',
                       ])

    def test_escaping_markup_token_should_make_contents_be_treated_as_normal_paragraph(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('@literal{ line')])],
                            sut.parse(['\\@literal{',
                                       'line',
                                       ]))

    def test_escaping_backslash(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.StringText('\\@literal{ line')])],
                            sut.parse(['\\\\@literal{',
                                       'line',
                                       ]))

    def test_literal_block_with_blank_lines_should_not_split_block(self):
        test_resource.check(self,
                            [sut.LiteralLayout(lines_content(['first line'] +
                                                             sut.PARAGRAPH_SEPARATOR_LINES +
                                                             ['last line']))],
                            sut.parse(['@literal{',
                                       'first line'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['last line',
                                       '@}',
                                       ]))

    def test_literal_block_between_paragraph_blocks(self):
        test_resource.check(self,
                            [
                                sut.Paragraph([sut.StringText('para 1')]),
                                sut.LiteralLayout(lines_content(['literal line'])),
                                sut.Paragraph([sut.StringText('para 2')]),
                            ],
                            sut.parse(['para 1'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['@literal{',
                                       'literal line',
                                       '@}'] +
                                      sut.PARAGRAPH_SEPARATOR_LINES +
                                      ['para 2']))


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
                            [sut.Paragraph([sut.StringText('para 1 text 1')]),
                             sut.Paragraph([sut.StringText('para 2 text 1'),
                                            sut.StringText('para 2 text 2'),
                                            sut.StringText('para 2 text 3')])],
                            actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseEmpty))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraphWithSingleText))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraphWithMultipleTexts))
    ret_val.addTest(unittest.makeSuite(TestMultipleParagraphs))
    ret_val.addTest(unittest.makeSuite(TestMultipleParagraphsWithAlternateSeparator))
    ret_val.addTest(unittest.makeSuite(TestLiteral))

    ret_val.addTest(unittest.makeSuite(TestNormalize))

    ret_val.addTest(unittest.makeSuite(TestNormalizeAndParse))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
