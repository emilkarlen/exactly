from abc import ABC, abstractmethod
from pathlib import Path
from typing import Sequence, Optional, TypeVar, Generic

from exactly_lib.section_document.source_location import SourceLocation, SourceLocationInfo
from exactly_lib.util.line_source import LineSequence

T = TypeVar('T')


class ParseErrorVisitor(Generic[T], ABC):
    def visit(self):
        pass

    @abstractmethod
    def visit_file_source_error(self, ex: 'FileSourceError') -> T:
        pass

    @abstractmethod
    def visit_file_access_error(self, ex: 'FileAccessError') -> T:
        pass


class ParseError(Exception, ABC):
    """
    An exception from a document parser.
    """

    def __init__(self,
                 message: str,
                 location_path: Sequence[SourceLocation]):
        self._message = message
        self._location_path = location_path

    @property
    @abstractmethod
    def maybe_section_name(self) -> Optional[str]:
        pass

    @property
    def location_path(self) -> Sequence[SourceLocation]:
        return self._location_path

    @property
    def message(self) -> str:
        return self._message

    @abstractmethod
    def accept(self, visitor: ParseErrorVisitor[T]) -> T:
        pass


class FileSourceError(ParseError):
    """
    An exceptions related to a line in the test case.
    """

    def __init__(self,
                 source: LineSequence,
                 message: str,
                 maybe_section_name: Optional[str],
                 source_location_info: SourceLocationInfo):
        super().__init__(message,
                         list(source_location_info.source_location_path.file_inclusion_chain) +
                         [source_location_info.source_location_path.location])
        self._maybe_section_name = maybe_section_name
        self._source_location_info = source_location_info
        self._source = source
        self._message = message

    @property
    def maybe_section_name(self) -> Optional[str]:
        return self._maybe_section_name

    @property
    def source(self) -> LineSequence:
        return self._source

    @property
    def source_location_info(self) -> SourceLocationInfo:
        return self._source_location_info

    def accept(self, visitor: ParseErrorVisitor[T]) -> T:
        return visitor.visit_file_source_error(self)


class FileAccessError(ParseError):
    def __init__(self,
                 erroneous_path: Path,
                 message: str,
                 location_path: Sequence[SourceLocation],
                 section_name: Optional[str] = None,
                 ):
        super().__init__(message, location_path)
        self._erroneous_path = erroneous_path
        self._section_name = section_name

    @property
    def maybe_section_name(self) -> Optional[str]:
        return self._section_name

    @property
    def erroneous_path(self) -> Path:
        return self._erroneous_path

    def accept(self, visitor: ParseErrorVisitor[T]) -> T:
        return visitor.visit_file_access_error(self)
