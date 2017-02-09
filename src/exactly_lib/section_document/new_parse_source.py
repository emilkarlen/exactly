import unittest

from exactly_lib.util.line_source import Line


class ParseSource:
    """
    Source string with lookahead of the current line.
    """
    def __init__(self, source_string: str):
        self.source_string = source_string
        if self.source_string == '':
            self._current_line = None
        else:
            first_line_split = self.source_string.split(sep='\n', maxsplit=1)
            self._current_line = Line(1, first_line_split[0])

    @property
    def is_at_eof(self) -> bool:
        return self._current_line is None

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
    def remaining_source(self) -> str:
        return self.source_string

    def consume_current_line(self):
        first_line_split = self.source_string.split(sep='\n', maxsplit=1)
        if len(first_line_split) == 1:
            self._current_line = None
            self.source_string = ''
        else:
            next_line_num = self._current_line.line_number + 1
            self.source_string = first_line_split[1]
            first_line_split = self.source_string.split(sep='\n', maxsplit=1)
            self._current_line = Line(next_line_num, first_line_split[0])


class TestParseSource(unittest.TestCase):
    def _assert_current_line_is(self, line_number: int, line_text: str, source: ParseSource):
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
        self._assert_current_line_is(1, 'single line', source)
        self.assertEquals('single line', source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_two_line_source(self):
        original_source = 'first line' + '\n' + 'second line'
        source = ParseSource(original_source)
        self._assert_current_line_is(1, 'first line', source)
        self.assertEquals(original_source, source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_current_line_is(2, 'second line', source)
        self.assertEquals('second line', source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_first_line_is_empty(self):
        source = ParseSource('\n' + 'second line')
        self._assert_current_line_is(1, '', source)
        source.consume_current_line()
        self._assert_current_line_is(2, 'second line', source)
        self.assertEquals('second line', source.remaining_source,
                          'remaining source')
        source.consume_current_line()
        self._assert_is_at_eof(source)

    def test_last_line_is_empty(self):
        source = ParseSource('first line' + '\n')
        self._assert_current_line_is(1, 'first line', source)
        source.consume_current_line()
        self._assert_current_line_is(2, '', source)
        source.consume_current_line()
        self._assert_is_at_eof(source)
