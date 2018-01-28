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


def line_sequence_from_line(line: Line) -> LineSequence:
    return single_line_sequence(line.line_number, line.text)


class SourceLocation(tuple):
    """A location in a file."""

    def __new__(cls,
                source: LineSequence,
                file_path: pathlib.Path):
        """
        :param source: None iff source if not relevant
        :param file_path: None iff source does not originate from a file
        """
        return tuple.__new__(cls, (source, file_path))

    @property
    def source(self) -> LineSequence:
        """
        :return: None iff source if not relevant
        """
        return self[0]

    @property
    def file_path(self) -> pathlib.Path:
        """
        :return: None iff source does not originate from a file
        """
        return self[1]


class SourceLocationPath(tuple):
    """A location in a file, with file inclusion chain info."""

    def __new__(cls,
                location: SourceLocation,
                file_inclusion_chain: Sequence[SourceLocation]):
        return tuple.__new__(cls, (location, file_inclusion_chain))

    @property
    def location(self) -> SourceLocation:
        return self[0]

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        return self[1]


def source_location_path_of(file_path: pathlib.Path,
                            line: Line) -> SourceLocationPath:
    """
    :return: None iff file_path and line is None
    """
    if file_path is None and line is None:
        return None
    line_sequence = None
    if line:
        line_sequence = line_sequence_from_line(line)
    return source_location_path_without_inclusions(
        SourceLocation(line_sequence,
                       file_path)
    )


def source_location_path_without_inclusions(location: SourceLocation) -> SourceLocationPath:
    return SourceLocationPath(location, ())


def source_location_path_of_non_empty_location_path(location_path: Sequence[SourceLocation]) -> SourceLocationPath:
    return SourceLocationPath(location_path[-1],
                              location_path[:-1])
