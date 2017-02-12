import unittest

from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseSource)


class TestParseSource(unittest.TestCase):
    def _assert_current_line_and_remaining_part_of_it_is(self, line_number: int,
                                                         line_text: str,
                                                         source: ParseSource):
        self._assert_current_line_is(line_number, line_text, source)
        self.assertEquals(line_text,
                          source.remaining_part_of_current_line,
                          'Remaining part of current line')

    def _assert_current_line_is(self, line_number: int,
                                line_text: str,
                                source: ParseSource):
        self.assertEquals(line_text,
                          source.current_line_text,
                          'Text of current line')
        self.assertEquals(line_number,
                          source.current_line_number,
                          'Line number of current line')
        self.assertEquals(line_text,
                          source.current_line.text,
                          'Text of current line (extracted via Line)')
        self.assertEquals(line_number,
                          source.current_line.line_number,
                          'Line number of current line (extracted via Line)')

    def _assert_is_at_eof(self, source: ParseSource):
        self.assertTrue(source.is_at_eof)
        self.assertEquals('', source.remaining_source,
                          'remaining source')

    def _assert_is_at_eol(self, source: ParseSource):
        self.assertTrue(source.is_at_eol)
        self.assertEquals('', source.remaining_part_of_current_line,
                          'remaining_part_of_current_line')

    def test_empty_source(self):
        source = ParseSource('')
        self._assert_is_at_eof(source)
        self.assertTrue(source.has_current_line, 'has_current_line')
        self._assert_is_at_eol(source)
        self._assert_current_line_is(1, '', source)

    def test_source_with_single_line(self):
        source = ParseSource('single line')
        self.assertFalse(source.is_at_eof, 'is_at_eof')
        self.assertTrue(source.has_current_line, 'has_current_line')
        self.assertFalse(source.is_at_eol, 'is_at_eol')
        self._assert_current_line_is(1, 'single line', source)
        self.assertEquals('single line', source.remaining_source,
                          'remaining source')

    def test_consume_line_from_source_with_single_line(self):
        source = ParseSource('single line')
        source.consume_current_line()
        self.assertTrue(source.is_at_eof, 'is_at_eof')
        self.assertFalse(source.has_current_line, 'has_current_line')

    def test_consume_all_characters_of_first_line_from_source_with_single_line(self):
        source = ParseSource('single line')
        source.consume_part_of_current_line(len('single line'))
        self.assertTrue(source.is_at_eof, 'is_at_eof')
        self.assertTrue(source.has_current_line, 'has_current_line')
        self.assertTrue(source.is_at_eol, 'is_at_eol')
        self.assertEquals('', source.remaining_source,
                          'remaining source')

    def test_consume_all_characters_from_source_with_single_line(self):
        source = ParseSource('single line')
        source.consume(len('single line'))
        self.assertTrue(source.is_at_eof, 'is_at_eof')
        self.assertTrue(source.has_current_line, 'has_current_line')
        self.assertTrue(source.is_at_eol, 'is_at_eol')
        self.assertEquals('', source.remaining_source,
                          'remaining source')

    def test_when_source_is_empty_then_it_should_indicate_eof(self):
        source = ParseSource('')
        self._assert_is_at_eof(source)

    def test_when_source_is_empty_then_it_should_not_indicate_eof(self):
        source = ParseSource('non-empty')
        self.assertFalse(source.is_at_eof)

    def test_single_line_source(self):
        source = ParseSource('single line')
        self._assert_current_line_and_remaining_part_of_it_is(1, 'single line', source)
        self.assertEquals('single line', source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_two_line_source(self):
        original_source = 'first line' + '\n' + 'second line'
        source = ParseSource(original_source)
        self._assert_current_line_and_remaining_part_of_it_is(1, 'first line', source)
        self.assertEquals(original_source, source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_current_line_and_remaining_part_of_it_is(2, 'second line', source)
        self.assertEquals('second line', source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_first_line_is_empty(self):
        source = ParseSource('\n' + 'second line')
        self._assert_current_line_and_remaining_part_of_it_is(1, '', source)
        source.consume_current_line()
        self._assert_current_line_and_remaining_part_of_it_is(2, 'second line', source)
        self.assertEquals('second line', source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_last_line_is_empty(self):
        source = ParseSource('first line' + '\n')
        self._assert_current_line_and_remaining_part_of_it_is(1, 'first line', source)
        source.consume_current_line()
        self._assert_current_line_and_remaining_part_of_it_is(2, '', source)
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_consume_part_of_current_line(self):
        source = ParseSource('first line' + '\n' + 'second line')
        source.consume_part_of_current_line(len('first') + 1)
        self._assert_current_line_is(1, 'first line', source)
        self.assertEqual('line', source.remaining_part_of_current_line,
                         'Remaining part of current line')
        self.assertEqual('line' + '\n' + 'second line',
                         source.remaining_source,
                         'Remaining source')
        self.assertFalse(source.is_at_eof, 'is_at_eof')
        self.assertFalse(source.is_at_eol, 'is_at_eol')

    def test_consume_part_of_current_line__until_end_of_line_of_last_line(self):
        source = ParseSource('first line')
        source.consume_part_of_current_line(len('first line'))
        self._assert_current_line_is(1, 'first line', source)
        self.assertTrue(source.is_at_eol, 'is_at_eol')
        self.assertTrue(source.is_at_eof, 'is_at_eof')
        self.assertEqual('', source.remaining_part_of_current_line,
                         'Remaining part of current line')
        self.assertEqual('',
                         source.remaining_source,
                         'Remaining source')

    def test_raise_exception_when_too_many_characters_are_consumed(self):
        source = ParseSource('first line' + '\n' + 'second line')
        with self.assertRaises(ValueError):
            source.consume_part_of_current_line(len('first line') + 1)
            self.assertEquals('first line', source.remaining_part_of_current_line,
                              'remaining_part_of_current_line should not have been updated')

    def test_is_at_eol_should_be_false_if_is_not_at_eol(self):
        source = ParseSource('non empty line')
        self.assertFalse(source.is_at_eol,
                         'is_at_eol')

    def test_is_at_eol_should_be_true_if_is_at_eol(self):
        source = ParseSource('' + '\n' + 'second line')
        self.assertTrue(source.is_at_eol,
                        'is_at_eol')

    def test_is_at_eol_should_be_false_after_consuming_a_line_if_the_following_line_is_non_empty(self):
        source = ParseSource('' + '\n' + 'second line')
        source.consume_current_line()
        self.assertFalse(source.is_at_eol,
                         'is_at_eol')

    def test_consume_initial_space(self):
        test_cases = [
            (['', 'second line'], '', True),
            (['non-space', 'second line'], 'non-space', False),
            (['   ', 'second line'], '', True),
            (['   non-space', 'second line'], 'non-space', False),
        ]
        for lines, remaining_part, is_at_eol in test_cases:
            with self.subTest():
                source_lines = '\n'.join(lines)
                source = ParseSource(source_lines)
                source.consume_initial_space_on_current_line()
                self.assertEquals(is_at_eol, source.is_at_eol,
                                  'is_at_eol')
                self.assertEqual(remaining_part, source.remaining_part_of_current_line,
                                 'remaining_part_of_current_line')
                self._assert_current_line_is(1, lines[0], source)

    def test_consume_with_invalid_arguments(self):
        test_cases = [
            ('a', 0, 2),
            ('a', 1, 1),
            ('a\nb', 0, 4),
            ('a\nb', 1, 3),
        ]
        for source, num_chars_on_current_line_to_consume_before_check, num_chars in test_cases:
            with self.subTest(source=source, num_chars=num_chars):
                source = ParseSource(source)
                source.consume_part_of_current_line(num_chars_on_current_line_to_consume_before_check)
                with self.assertRaises(ValueError):
                    source.consume(num_chars)

    def test_consume_with_valid_arguments(self):
        test_cases = [
            (TestSetupForConsume('one whole line and part of next, with one line remaining',
                                 source_lines=['123',
                                               '45',
                                               '6'],
                                 number_of_characters_to_consume_from_current_line_before_test=0,
                                 number_of_characters_to_consume=4 + 1),
             assert_source(is_at_eof=asrt.equals(False),
                           is_at_eol=asrt.equals(False),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           remaining_part_of_current_line=asrt.equals('5'),
                           remaining_source=asrt.equals('5\n6'))),
            (TestSetupForConsume('one whole line and part of next, with one line remaining, on column index 1',
                                 source_lines=['123',
                                               '45',
                                               '6'],
                                 number_of_characters_to_consume_from_current_line_before_test=1,
                                 number_of_characters_to_consume=4 + 1 - 1),
             assert_source(is_at_eof=asrt.equals(False),
                           is_at_eol=asrt.equals(False),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           remaining_part_of_current_line=asrt.equals('5'),
                           remaining_source=asrt.equals('5\n6'))),
            (TestSetupForConsume('two whole lines, with one line remaining',
                                 source_lines=['123',
                                               '45',
                                               '6'],
                                 number_of_characters_to_consume_from_current_line_before_test=0,
                                 number_of_characters_to_consume=5 + 1),
             assert_source(is_at_eof=asrt.equals(False),
                           is_at_eol=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           remaining_part_of_current_line=asrt.equals(''),
                           remaining_source=asrt.equals('\n6'))),
            (TestSetupForConsume('two whole lines, with one line remaining, on column index 2',
                                 source_lines=['123',
                                               '45',
                                               '6'],
                                 number_of_characters_to_consume_from_current_line_before_test=2,
                                 number_of_characters_to_consume=5 + 1 - 2),
             assert_source(is_at_eof=asrt.equals(False),
                           is_at_eol=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           remaining_part_of_current_line=asrt.equals(''),
                           remaining_source=asrt.equals('\n6'))),
            (TestSetupForConsume('two whole lines, with no line after',
                                 source_lines=['123',
                                               '45'],
                                 number_of_characters_to_consume_from_current_line_before_test=0,
                                 number_of_characters_to_consume=5 + 1),
             assert_source(is_at_eof=asrt.equals(True),
                           is_at_eol=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           remaining_part_of_current_line=asrt.equals(''),
                           remaining_source=asrt.equals(''))),
            (TestSetupForConsume('two whole lines, with no line after, on column index 3',
                                 source_lines=['123',
                                               '45'],
                                 number_of_characters_to_consume_from_current_line_before_test=3,
                                 number_of_characters_to_consume=5 + 1 - 3),
             assert_source(is_at_eof=asrt.equals(True),
                           is_at_eol=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           remaining_part_of_current_line=asrt.equals(''),
                           remaining_source=asrt.equals(''))),
        ]
        for setup, assertion in test_cases:
            with self.subTest(case_name=setup.name):
                source_lines = '\n'.join(setup.source_lines)
                source = ParseSource(source_lines)
                source.consume_part_of_current_line(setup.number_of_characters_to_consume_from_current_line_before_test)
                source.consume(setup.number_of_characters_to_consume)
                assertion.apply(self, source, asrt.MessageBuilder(setup.name))


class TestSetupForConsume:
    def __init__(self,
                 name: str,
                 source_lines: list,
                 number_of_characters_to_consume_from_current_line_before_test: int,
                 number_of_characters_to_consume: int):
        self.name = name
        self.source_lines = source_lines
        self.number_of_characters_to_consume = number_of_characters_to_consume
        self.number_of_characters_to_consume_from_current_line_before_test = \
            number_of_characters_to_consume_from_current_line_before_test
