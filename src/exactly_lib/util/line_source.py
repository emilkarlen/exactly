import os
import pathlib
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


def single_line_sequence(line_number: int, line: str) -> LineSequence:
    return LineSequence(line_number, (line,))


class LineInFile(tuple):
    def __new__(cls,
                line: Line,
                file_path: pathlib.Path):
        return tuple.__new__(cls, (line, file_path))

    @property
    def line(self) -> Line:
        return self[0]

    @property
    def file_path(self) -> pathlib.Path:
        return self[1]


class SourceLocation(tuple):
    """A location in a file."""

    def __new__(cls,
                source: LineSequence,
                file_path: pathlib.Path):
        return tuple.__new__(cls, (source, file_path))

    @property
    def source(self) -> LineSequence:
        return self[0]

    @property
    def file_path(self) -> pathlib.Path:
        return self[1]
