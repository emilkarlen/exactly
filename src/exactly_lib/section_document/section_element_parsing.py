from typing import Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import line_sequence_from_line


class SourceError(Exception):
    """
    An exceptions related to a line in the test case,
    raised by a parser that is unaware of current file and section.

    I.e., this exception is used within the parsing of a document,
    as communication between the parsing framework and element parsers.

    This kind of exceptions is never thrown from a document parser.
    """

    def __init__(self,
                 source: line_source.LineSequence,
                 message: str):
        self._source = source
        self._message = message

    @property
    def source(self) -> line_source.LineSequence:
        return self._source

    @property
    def message(self) -> str:
        return self._message


def new_source_error_of_single_line(line: line_source.Line,
                                    message: str) -> SourceError:
    return SourceError(line_sequence_from_line(line),
                       message)


class SectionElementParser:
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        """
        May return None if source is not recognized.
        Unrecognized source may also be reported by raising SourceError.

        The possibility to return None exists to help constructing parsers from parts -
        a return value of None means that some other parser may try to parse the same source,
        while a raised SourceError means that this parser recognizes the source (e.g. by
        being the name of an instruction), but that there is some syntax error related to
        the recognized element (e.g. instruction).

        :param fs_location_info: Information about the location of the source file being parsed
        :param source: Remaining source to parse

        :returns: None iff source is invalid / unrecognized. If None is returned, source must _not_
        have been consumed.
        :raises SourceError: The element cannot be parsed.
        """
        raise NotImplementedError('abstract method')
