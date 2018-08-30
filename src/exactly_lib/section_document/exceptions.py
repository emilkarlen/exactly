from pathlib import Path
from typing import Sequence, Optional

from exactly_lib.section_document.section_element_parsing import SectionElementError
from exactly_lib.section_document.source_location import SourceLocation, SourceLocationInfo


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
                 source_error: SectionElementError,
                 maybe_section_name: Optional[str],
                 source_location_info: SourceLocationInfo):
        super().__init__(source_error.message,
                         list(source_location_info.source_location_path.file_inclusion_chain) +
                         [source_location_info.source_location_path.location])
        self._maybe_section_name = maybe_section_name
        self._source_error = source_error
        self._source_location_info = source_location_info

    @property
    def maybe_section_name(self) -> Optional[str]:
        return self._maybe_section_name

    @property
    def source_error(self) -> SectionElementError:
        return self._source_error

    @property
    def error_message(self) -> str:
        return self._source_error.message

    @property
    def source_location_info(self) -> SourceLocationInfo:
        return self._source_location_info


class FileAccessError(ParseError):
    def __init__(self,
                 erroneous_path: Path,
                 message: str,
                 location_path: Sequence[SourceLocation]):
        super().__init__(message, location_path)
        self._erroneous_path = erroneous_path

    @property
    def erroneous_path(self) -> Path:
        return self._erroneous_path
