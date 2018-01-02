import pathlib
from typing import Sequence

from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocation


class SourceError(Exception):
    """
    An exceptions related to a line in the test case,
    raised by a parser that is unaware of current section.

    I.e., this exception is used within the parsing of a document,
    as communication between the parsing framework and element parsers.

    This kind of exceptions is never thrown from a document parser.
    """

    def __init__(self,
                 line: line_source.Line,
                 message: str):
        self._line = line
        self._message = message

    @property
    def line(self) -> line_source.Line:
        return self._line

    @property
    def source(self) -> line_source.LineSequence:
        # TODO Objects should store LineSequence instead of Line
        return line_source.single_line_sequence(self._line.line_number,
                                                self._line.text)

    @property
    def message(self) -> str:
        return self._message


def new_source_error(source: line_source.LineSequence,
                     message: str) -> SourceError:
    return SourceError(source.first_line,
                       message)


class ParseError(Exception):
    """
    An exception from a document parser.
    """

    def __init__(self,
                 message: str,
                 location_path: Sequence[SourceLocation]):
        self._message = message
        self._location_path = location_path

    @property
    def location_path(self) -> Sequence[SourceLocation]:
        return self._location_path

    @property
    def message(self) -> str:
        return self._message


class FileSourceError(ParseError):
    """
    An exceptions related to a line in the test case.
    """

    def __init__(self,
                 source_error: SourceError,
                 maybe_section_name: str,
                 location_path: Sequence[SourceLocation]):
        super().__init__(source_error.message,
                         location_path)
        self._source_error = source_error
        self._maybe_section_name = maybe_section_name

    @property
    def source_error(self) -> SourceError:
        return self._source_error

    @property
    def maybe_section_name(self) -> str:
        return self._maybe_section_name


class FileAccessError(ParseError):
    def __init__(self,
                 erroneous_path: pathlib.Path,
                 message: str,
                 location_path: Sequence[SourceLocation]):
        super().__init__(message, location_path)
        self._erroneous_path = erroneous_path

    @property
    def erroneous_path(self) -> pathlib.Path:
        return self._erroneous_path
