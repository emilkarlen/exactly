import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseSource)


class TestParseSource(unittest.TestCase):
    test_cases_for_consume_all_characters_of_current_line = [
        ('single line',
         assert_source(is_at_eof=asrt.is_true,
                       has_current_line=asrt.is_true,
                       column_index=asrt.equals(len('single line')),
                       is_at_eol=asrt.is_true,
                       is_at_eol__except_for_space=asrt.is_true,
                       remaining_source=asrt.equals(''))
         ),
        ('',
         assert_source(is_at_eof=asrt.is_true,
                       has_current_line=asrt.is_true,
                       column_index=asrt.equals(0),
                       is_at_eol=asrt.is_true,
                       is_at_eol__except_for_space=asrt.is_true,
                       remaining_source=asrt.equals(''))
         ),
        ('first line\nsecond line',
         assert_source(is_at_eof=asrt.is_false,
                       has_current_line=asrt.is_true,
                       is_at_eol=asrt.is_true,
                       is_at_eol__except_for_space=asrt.is_true,
                       current_line_number=asrt.equals(1),
                       current_line_text=asrt.equals('first line'),
                       column_index=asrt.equals(len('first line')),
                       remaining_source=asrt.equals('\nsecond line'))
         ),
        ('single line\n',
         assert_source(is_at_eof=asrt.is_false,
                       has_current_line=asrt.is_true,
                       is_at_eol=asrt.is_true,
                       is_at_eol__except_for_space=asrt.is_true,
                       current_line_number=asrt.equals(1),
                       current_line_text=asrt.equals('single line'),
                       column_index=asrt.equals(len('single line')),
                       remaining_source=asrt.equals('\n'))
         ),
        ('\n',
         assert_source(is_at_eof=asrt.is_false,
                       has_current_line=asrt.is_true,
                       is_at_eol=asrt.is_true,
                       is_at_eol__except_for_space=asrt.is_true,
                       current_line_number=asrt.equals(1),
                       current_line_text=asrt.equals(''),
                       column_index=asrt.equals(0),
                       remaining_source=asrt.equals('\n'))
         ),
        ('\nsecond line',
         assert_source(is_at_eof=asrt.is_false,
                       has_current_line=asrt.is_true,
                       is_at_eol=asrt.is_true,
                       is_at_eol__except_for_space=asrt.is_true,
                       current_line_number=asrt.equals(1),
                       current_line_text=asrt.equals(''),
                       column_index=asrt.equals(0),
                       remaining_source=asrt.equals('\nsecond line'))
         ),
    ]

    def _assert_current_line_and_remaining_part_of_it_is(self, line_number: int,
                                                         line_text: str,
                                                         source: ParseSource):
        self._assert_current_line_is(line_number, line_text, source)
        self.assertEqual(line_text,
                         source.remaining_part_of_current_line,
                         'Remaining part of current line')

    def _assert_current_line_is(self, line_number: int,
                                line_text: str,
                                source: ParseSource):
        self.assertEqual(line_text,
                         source.current_line_text,
                         'Text of current line')
        self.assertEqual(line_number,
                         source.current_line_number,
                         'Line number of current line')
        self.assertEqual(line_text,
                         source.current_line.text,
                         'Text of current line (extracted via Line)')
        self.assertEqual(line_number,
                         source.current_line.line_number,
                         'Line number of current line (extracted via Line)')

    def _assert_is_at_eof(self, source: ParseSource):
        self.assertTrue(source.is_at_eof)
        self.assertEqual('', source.remaining_source,
                         'remaining source')

    def _assert_is_at_eol(self, source: ParseSource):
        self.assertTrue(source.is_at_eol)
        self.assertEqual('', source.remaining_part_of_current_line,
                         'remaining_part_of_current_line')

    def test_construction(self):
        test_cases = [
            ('single line',
             assert_source(is_at_eof=asrt.is_false,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           has_current_line=asrt.is_true,
                           column_index=asrt.equals(0),
                           current_line_number=asrt.equals(1),
                           current_line_text=asrt.equals('single line'))
             ),
            ('',
             assert_source(is_at_eof=asrt.is_true,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           has_current_line=asrt.is_true,
                           column_index=asrt.equals(0),
                           current_line_number=asrt.equals(1),
                           current_line_text=asrt.equals(''))
             ),
            ('first line\nsecond line',
             assert_source(is_at_eof=asrt.is_false,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           has_current_line=asrt.is_true,
                           column_index=asrt.equals(0),
                           current_line_number=asrt.equals(1),
                           current_line_text=asrt.equals('first line'))
             ),
            ('single line\n',
             assert_source(is_at_eof=asrt.is_false,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           has_current_line=asrt.is_true,
                           column_index=asrt.equals(0),
                           current_line_number=asrt.equals(1),
                           current_line_text=asrt.equals('single line'))
             ),
            ('\n',
             assert_source(is_at_eof=asrt.is_false,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           has_current_line=asrt.is_true,
                           column_index=asrt.equals(0),
                           current_line_number=asrt.equals(1),
                           current_line_text=asrt.equals(''))
             ),
            ('\nsecond line',
             assert_source(is_at_eof=asrt.is_false,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           has_current_line=asrt.is_true,
                           column_index=asrt.equals(0),
                           current_line_number=asrt.equals(1),
                           current_line_text=asrt.equals(''))
             ),
        ]
        for source_string, expectation in test_cases:
            with self.subTest(msg='construction:' + repr(source_string)):
                source = ParseSource(source_string)
                expectation.apply_with_message(self, source, 'construction:{}'.format(repr(source_string)))

    def test_only_newline2(self):
        source = ParseSource('\n\n')
        source.consume_current_line()
        self.assertFalse(source.is_at_eof)
        self.assertTrue(source.has_current_line, 'has_current_line')
        self._assert_is_at_eol(source)
        self._assert_current_line_is(2, '', source)

    def test_consume_current_line(self):
        test_cases = [
            ('single line',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_false,
                           remaining_source=asrt.equals(''))
             ),
            ('',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_false)
             ),
            ('first line\nsecond line',
             assert_source(is_at_eof=asrt.is_false,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('second line'),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals('second line'))
             ),
            ('single line\n',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals(''),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals(''))
             ),
            ('\n',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals(''),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals(''))
             ),
            ('\nsecond line',
             assert_source(is_at_eof=asrt.is_false,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('second line'),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals('second line'))
             ),
        ]
        for source_string, expectation in test_cases:
            with self.subTest(msg='consume current line: ' + repr(source_string)):
                source = ParseSource(source_string)
                source.consume_current_line()
                expectation.apply_with_message(self, source, 'consume_current_line:{}'.format(repr(source_string)))

    def test_consume_part_of_current_line__consume_all_characters(self):
        for source_string, expectation in self.test_cases_for_consume_all_characters_of_current_line:
            with self.subTest(msg='consume_part_of_current_line: ' + repr(source_string)):
                source = ParseSource(source_string)
                source.consume_part_of_current_line(len(source.current_line_text))
                expectation.apply_with_message(self, source,
                                               'consume_part_of_current_line:{}'.format(repr(source_string)))

    def test_consume__consume_all_characters_of_current_line(self):
        for source_string, expectation in self.test_cases_for_consume_all_characters_of_current_line:
            with self.subTest(msg='consume: ' + repr(source_string)):
                source = ParseSource(source_string)
                source.consume(len(source.current_line_text))
                expectation.apply_with_message(self, source, 'consume:{}'.format(repr(source_string)))

    def test_consume__consume_all_characters_of_current_line_plus_one(self):
        test_cases = [
            ('first line\nsecond line',
             assert_source(is_at_eof=asrt.is_false,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('second line'),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals('second line'))
             ),
            ('single line\n',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals(''),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals(''))
             ),
            ('\n',
             assert_source(is_at_eof=asrt.is_true,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_true,
                           is_at_eol__except_for_space=asrt.is_true,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals(''),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals(''))
             ),
            ('\nsecond line',
             assert_source(is_at_eof=asrt.is_false,
                           has_current_line=asrt.is_true,
                           is_at_eol=asrt.is_false,
                           is_at_eol__except_for_space=asrt.is_false,
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('second line'),
                           column_index=asrt.equals(0),
                           remaining_source=asrt.equals('second line'))
             ),
        ]
        for source_string, expectation in test_cases:
            with self.subTest(msg='consume len(current line)+1: ' + repr(source_string)):
                source = ParseSource(source_string)
                source.consume(1 + len(source.current_line_text))
                expectation.apply_with_message(self, source,
                                               'consume len(current line)+1:{}'.format(repr(source_string)))

    def test_single_line_source(self):
        source = ParseSource('single line')
        self._assert_current_line_and_remaining_part_of_it_is(1, 'single line', source)
        self.assertEqual('single line', source.remaining_source,
                         'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_two_line_source(self):
        original_source = 'first line' + '\n' + 'second line'
        source = ParseSource(original_source)
        self._assert_current_line_and_remaining_part_of_it_is(1, 'first line', source)
        self.assertEqual(original_source, source.remaining_source,
                         'remaining source')
        source.consume_current_line()
        self._assert_current_line_and_remaining_part_of_it_is(2, 'second line', source)
        self.assertEqual('second line', source.remaining_source,
                         'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_first_line_is_empty(self):
        source = ParseSource('\n' + 'second line')
        self._assert_current_line_and_remaining_part_of_it_is(1, '', source)
        source.consume_current_line()
        self._assert_current_line_and_remaining_part_of_it_is(2, 'second line', source)
        self.assertEqual('second line', source.remaining_source,
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
            self.assertEqual('first line', source.remaining_part_of_current_line,
                             'remaining_part_of_current_line should not have been updated')

    def test_consume_initial_space(self):
        test_cases = [
            (['', 'second line'], '', True),
            (['non-space', 'second line'], 'non-space', False),
            (['   ', 'second line'], '', True),
            (['   non-space', 'second line'], 'non-space', False),
        ]
        for lines, remaining_part, is_at_eol in test_cases:
            with self.subTest():
                first_line = lines[0]
                source_lines = '\n'.join(lines)
                # ACT #
                source = ParseSource(source_lines)
                # ASSERT #
                source.consume_initial_space_on_current_line()
                assertion = assert_source(is_at_eol=asrt.equals(is_at_eol),
                                          remaining_part_of_current_line=asrt.equals(remaining_part),
                                          current_line_number=asrt.equals(1),
                                          current_line_text=asrt.equals(lines[0]),
                                          column_index=asrt.equals(len(first_line) - len(first_line.lstrip()))
                                          )
                assertion.apply(self, source)

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
                           is_at_eol__except_for_space=asrt.equals(False),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           column_index=asrt.equals(1),
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
                           is_at_eol__except_for_space=asrt.equals(False),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           column_index=asrt.equals(1),
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
                           is_at_eol__except_for_space=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           column_index=asrt.equals(2),
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
                           is_at_eol__except_for_space=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           column_index=asrt.equals(2),
                           remaining_part_of_current_line=asrt.equals(''),
                           remaining_source=asrt.equals('\n6'))),
            (TestSetupForConsume('two whole lines, with no line after',
                                 source_lines=['123',
                                               '45'],
                                 number_of_characters_to_consume_from_current_line_before_test=0,
                                 number_of_characters_to_consume=5 + 1),
             assert_source(is_at_eof=asrt.equals(True),
                           is_at_eol=asrt.equals(True),
                           is_at_eol__except_for_space=asrt.equals(True),
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
                           is_at_eol__except_for_space=asrt.equals(True),
                           has_current_line=asrt.equals(True),
                           current_line_number=asrt.equals(2),
                           current_line_text=asrt.equals('45'),
                           column_index=asrt.equals(2),
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

    def test_catch_up_with(self):
        test_cases = [
            (['abc'],
             lambda parse_source: parse_source.consume(1),
             lambda parse_source: parse_source.consume(2)),
            (['abc', 'def'],
             lambda parse_source: None,
             lambda parse_source: parse_source.consume_current_line()),
            (['123', '456'],
             lambda parse_source: None,
             lambda parse_source: parse_source.consume(5)),
            (['123', '456'],
             lambda parse_source: None,
             lambda parse_source: parse_source.consume(7)),
        ]
        for original_source_lines, original_setup, copy_modifier in test_cases:
            with self.subTest():
                # ARRANGE #
                original = ParseSource('\n'.join(original_source_lines))
                original_setup(original)
                # ACT #
                copy = original.copy
                copy_modifier(copy)
                original.catch_up_with(copy)
                # ASSERT #
                self.assertEqual(copy.remaining_source,
                                 original.remaining_source,
                                 'remaining_source')
                self.assertEqual(copy.current_line_number,
                                 original.current_line_number,
                                 'current_line_number')
                self.assertEqual(copy.remaining_part_of_current_line,
                                 original.remaining_part_of_current_line,
                                 'remaining_part_of_current_line')
                self.assertEqual(copy.column_index,
                                 original.column_index,
                                 'column_index')


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
