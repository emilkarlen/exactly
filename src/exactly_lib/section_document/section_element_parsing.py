from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import line_sequence_from_line


class SectionElementError(Exception):
    """
    An exceptions related to a line in the test case that is
    expected to be parsed as a :class:SectionElement

    Does not need to be aware of current file and section,
    since this is taken care of by the document parsing framework.

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


class UnrecognizedSectionElementSourceError(SectionElementError):
    """
    The source is not recognized by the parser,
    but may be recognized by another parser.

    The parser must not have consumed any source.
    """
    pass


class RecognizedSectionElementSourceError(SectionElementError):
    """
    The source is recognized, in the meaning that the element
    should be parsed by the parser raising this exception.

    But the element source contains an unrecoverable error,
    e.g. a syntax error in the arguments to a recognized instruction.

    The parser may have consumed source.
    """
    pass


def new_unrecognized_section_element_error_of_single_line(line: line_source.Line,
                                                          message: str) -> SectionElementError:
    return UnrecognizedSectionElementSourceError(line_sequence_from_line(line),
                                                 message)


def new_recognized_section_element_error_of_single_line(line: line_source.Line,
                                                        message: str) -> SectionElementError:
    return RecognizedSectionElementSourceError(line_sequence_from_line(line),
                                               message)


T = TypeVar('T')


class LocationAwareParser(Generic[T], ABC):
    @abstractmethod
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource,
              ) -> T:
        """
        :param fs_location_info: Information about the location of the source file being parsed
        :param source: Remaining source to parse
        """
        pass


class SectionElementParser(LocationAwareParser[Optional[ParsedSectionElement]], ABC):
    @abstractmethod
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        """
        Parser of a section element, represented by a :class:ParsedSectionElement

        The possibility to return None exists to help constructing parsers from parts -
        a return value of None means that some other parser may try to parse the same source,
        while a raised SourceError means that this parser recognizes the source (e.g. by
        being the name of an instruction), but that there is some syntax error related to
        the recognized element (e.g. instruction).

        :param fs_location_info: Information about the location of the source file being parsed
        :param source: Remaining source to parse

        :returns: None iff source is invalid / unrecognized. If None is returned, source must _not_
        have been consumed.
        :raises SectionElementError: The element cannot be parsed.
        """
        pass
