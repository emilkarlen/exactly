import os
from typing import Sequence


class Line(tuple):
    def __new__(cls,
                line_number: int,
                text: str):
        return tuple.__new__(cls, (line_number, text))

    @property
    def line_number(self) -> int:
        return self[0]

    @property
    def text(self) -> str:
        return self[1]


class LineSequence:
    """
    One or more consecutive lines.
    """

    def __init__(self,
                 first_line_number: int,
                 lines: Sequence[str]):
        """
        :param first_line_number: Line number of first line in the sequence.
        :param lines: Non-empty list of individual lines, without ending line-separator.
        """
        self._first_line_number = first_line_number
        self._lines = lines

    @property
    def first_line_number(self) -> int:
        return self._first_line_number

    @property
    def lines(self) -> Sequence[str]:
        """
        All lines (at least one). No line ends with the line-separator.
        """
        return self._lines

    @property
    def first_line(self) -> Line:
        return Line(self._first_line_number, self._lines[0])

    @property
    def text(self) -> str:
        """
        All lines, separated by line-separator, but not ending with one.
        """
        return os.linesep.join(self._lines)

    def __str__(self):
        return 'LineSequence({}, {})'.format(self.first_line_number,
                                             self.lines)


def single_line_sequence(line_number: int, line: str) -> LineSequence:
    return LineSequence(line_number, (line,))


def line_sequence_from_line(line: Line) -> LineSequence:
    return single_line_sequence(line.line_number, line.text)
