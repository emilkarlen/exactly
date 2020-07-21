import copy

from exactly_lib.util.line_source import Line


class ParseSource:
    """
    Source string with buffer for the current line.

    Lines are separated by \n.
    The number of lines
       = 1                (if source is empty)
       = number of \n + 1 (if last line is not empty)
       = number of \n     (if last line is     empty)
    (this means there is always at least one line, even though the source string is empty!)
    """

    def __init__(self, source_string: str):
        self._column_index = 0
        self.source_string = source_string
        first_line_split = self.source_string.split(sep='\n', maxsplit=1)
        self._current_line_number = 1
        self._current_line_text = first_line_split[0]

    @property
    def copy(self):
        return copy.copy(self)

    @property
    def is_at_eof(self) -> bool:
        return self._current_line_number is None or self._column_index == len(self.source_string)

    @property
    def has_current_line(self) -> bool:
        """
        Tells if there is a current line.
        Note that there may exist a current line even though is_at_eof.
        In that case, the current line can be consumed, and then both not(has_current_line) and is_at_eof.
        """
        return self._current_line_number is not None

    @property
    def is_at_eol(self) -> bool:
        """
        Precondition: has_current_line
        """
        return self._column_index == len(self._current_line_text)

    @property
    def is_at_eol__except_for_space(self) -> bool:
        """
        Precondition: has_current_line
        """
        s = self.remaining_part_of_current_line
        return not s or s.isspace()

    @property
    def current_line_number(self) -> int:
        """
        Precondition: has_current_line
        """
        return self._current_line_number

    @property
    def column_index(self) -> int:
        """
        Precondition: has_current_line
        """
        return self._column_index

    @property
    def current_line_text(self) -> str:
        """
        Precondition: has_current_line
        """
        return self._current_line_text

    @property
    def current_line(self) -> Line:
        """
        Precondition: has_current_line
        """
        return Line(self._current_line_number, self._current_line_text)

    @property
    def remaining_part_of_current_line(self) -> str:
        return self._current_line_text[self._column_index:]

    @property
    def remaining_source(self) -> str:
        return self.source_string[self._column_index:]

    def consume_part_of_current_line(self, num_characters: int):
        """
        The current line must have at least specified number of characters left.
        """
        n = self._column_index + num_characters
        if n > len(self._current_line_text):
            raise ValueError('Line does not contain specified number of characters to consume: ' +
                             str(num_characters))
        self._column_index = n

    def consume_initial_space_on_current_line(self):
        while self._column_index < len(self._current_line_text):
            if self.current_line_text[self._column_index].isspace():
                self._column_index += 1
            else:
                break

    def consume_current_line(self):
        if not self.has_current_line:
            raise ValueError('Cannot consume current line when there not has_current_line')
        self._column_index = 0
        first_line_split = self.source_string.split(sep='\n', maxsplit=1)
        if len(first_line_split) == 1:
            self._current_line_number = None
            self._current_line_text = None
            self.source_string = ''
        else:
            self.source_string = first_line_split[1]
            first_line_split = self.source_string.split(sep='\n', maxsplit=1)
            self._current_line_number += 1
            self._current_line_text = first_line_split[0]

    def consume(self, number_of_characters: int):
        """
        Consumes arbitrary number of characters and lines.

        Current line is updated according to number of lines consumed

        Number of lines consumed = number of \n consumed.
        This means that if the current line is the last line, then no lines will be consumed.

        :param number_of_characters: Each newline counts as 1.
        :except ValueError: number_of_characters > length of remaining source (newlines count as 1)
        """
        if number_of_characters > (len(self.source_string) - self._column_index):
            raise ValueError('Requested number-of-characters ({}) > length of remaining source ({})'
                             .format(number_of_characters,
                                     len(self.source_string) - self._column_index))
        remaining_source = self.source_string[self._column_index:]
        num_lines_consumed = remaining_source.count('\n', 0, number_of_characters)
        if num_lines_consumed == 0:
            self._column_index += number_of_characters
        else:
            index_of_1st_char_on_new_current_line = _index_of_1st_char_on_new_current_line(remaining_source,
                                                                                           number_of_characters)
            self.source_string = remaining_source[index_of_1st_char_on_new_current_line:]
            self._column_index = number_of_characters - index_of_1st_char_on_new_current_line
            first_line_split = self.source_string.split(sep='\n', maxsplit=1)
            self._current_line_number += num_lines_consumed
            self._current_line_text = first_line_split[0]

    def catch_up_with(self, parse_source_that_is_ahead: 'ParseSource'):
        """
        Consumes characters so that this source becomes identical to the given source.
        :param parse_source_that_is_ahead: Typically a source created as a copy of this source.
        """
        self._column_index = parse_source_that_is_ahead._column_index
        self.source_string = parse_source_that_is_ahead.source_string
        self._current_line_number = parse_source_that_is_ahead._current_line_number
        self._current_line_text = parse_source_that_is_ahead._current_line_text


def _index_of_1st_char_on_new_current_line(remaining_source: str, number_of_characters: int) -> int:
    return remaining_source.rindex('\n', 0, number_of_characters) + 1
