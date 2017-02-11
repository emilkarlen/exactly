import unittest

from exactly_lib.util.line_source import Line


class ParseSource:
    """
    Source string with lookahead of the current line.
    """

    def __init__(self, source_string: str):
        self._column_index = 0
        self.source_string = source_string
        if self.source_string == '':
            self._current_line = None
            self._current_line_len = None
        else:
            first_line_split = self.source_string.split(sep='\n', maxsplit=1)
            self._current_line = Line(1, first_line_split[0])
            self._current_line_len = len(self._current_line.text)

    @property
    def is_at_eof(self) -> bool:
        return self._current_line is None

    @property
    def is_at_eol(self) -> bool:
        """
        Precondition: not is_at_eof
        """
        return self._column_index == self._current_line_len

    @property
    def current_line_number(self) -> int:
        return self._current_line.line_number

    @property
    def current_line_text(self) -> str:
        return self._current_line.text

    @property
    def current_line(self) -> Line:
        return self._current_line

    @property
    def remaining_part_of_current_line(self) -> str:
        return self._current_line.text[self._column_index:]

    @property
    def remaining_source(self) -> str:
        return self.source_string[self._column_index:]

    def consume_part_of_current_line(self, num_characters: int):
        """
        The current line must have at least specified number of characters left.
        """
        n = self._column_index + num_characters
        if n > self._current_line_len:
            raise ValueError('Line does not contain specified number of characters to consume: ' +
                             str(num_characters))
        self._column_index = n

    def consume_initial_space_on_current_line(self):
        while self._column_index < self._current_line_len:
            if self.current_line_text[self._column_index].isspace():
                self._column_index += 1
            else:
                break

    def consume_current_line(self):
        self._column_index = 0
        first_line_split = self.source_string.split(sep='\n', maxsplit=1)
        if len(first_line_split) == 1:
            self._current_line = None
            self.source_string = ''
            self._current_line_len = None
        else:
            next_line_num = self._current_line.line_number + 1
            self.source_string = first_line_split[1]
            first_line_split = self.source_string.split(sep='\n', maxsplit=1)
            self._current_line = Line(next_line_num, first_line_split[0])
            self._current_line_len = len(self._current_line.text)


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
        self.assertFalse(source.is_at_eof,
                         'Expecting a current line to exist, but is at EOF')
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
