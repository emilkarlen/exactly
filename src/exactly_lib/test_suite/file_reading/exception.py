import pathlib
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic

from exactly_lib.definitions.test_suite import section_names_plain
from exactly_lib.section_document.exceptions import ParseError
from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath, \
    source_location_path_of_non_empty_location_path
from exactly_lib.util import line_source


class SuiteReadError(ABC, Exception):
    def __init__(self,
                 suite_file: pathlib.Path,
                 maybe_section_name: Optional[str] = None):
        self._suite_file = suite_file
        self._maybe_section_name = maybe_section_name

    @property
    def suite_file(self) -> pathlib.Path:
        return self._suite_file

    @property
    def maybe_section_name(self) -> Optional[str]:
        return self._maybe_section_name

    @property
    @abstractmethod
    def source_location(self) -> Optional[SourceLocationPath]:
        pass

    @property
    def source(self) -> Optional[line_source.LineSequence]:
        return (
            self.source_location.location.source
            if self.source_location
            else None
        )


class SuiteNonParseError(SuiteReadError, ABC):
    def __init__(self,
                 suite_file: pathlib.Path,
                 source: line_source.LineSequence,
                 maybe_section_name: Optional[str] = None):
        self._suite_file = suite_file
        self._source = source
        self._maybe_section_name = maybe_section_name

    @property
    def source(self) -> line_source.LineSequence:
        return self._source

    @property
    def source_location(self) -> SourceLocationPath:
        return SourceLocationPath(SourceLocation(self.source,
                                                 self.suite_file),
                                  [])


class SuiteDoubleInclusion(SuiteNonParseError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 source: line_source.LineSequence,
                 included_suite_file: pathlib.Path,
                 first_referenced_from: pathlib.Path):
        super().__init__(suite_file, source, section_names_plain.SECTION_NAME__SUITS)
        self._included_suite_file = included_suite_file
        self._first_referenced_from = first_referenced_from

    @property
    def included_suite_file(self) -> pathlib.Path:
        return self._included_suite_file

    @property
    def first_referenced_from(self) -> pathlib.Path:
        """
        The suite file that contains the first reference to the
        included file.
        :return: None iff the file was mentioned on the command line.
        """
        return self._first_referenced_from


class SuiteFileReferenceError(SuiteNonParseError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 section_name: str,
                 source: line_source.LineSequence,
                 reference: pathlib.Path,
                 error_message_header: str,
                 ):
        super().__init__(suite_file,
                         source,
                         section_name)
        self._reference = reference
        self.error_message_header = error_message_header

    @property
    def reference(self) -> pathlib.Path:
        return self._reference


class SuiteParseError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 document_parser_exception: ParseError):
        super().__init__(suite_file,
                         document_parser_exception.maybe_section_name)
        self._document_parser_exception = document_parser_exception

    @property
    def source_location(self) -> Optional[SourceLocationPath]:
        location_path = self._document_parser_exception.location_path
        return (source_location_path_of_non_empty_location_path(location_path)
                if location_path
                else None
                )

    @property
    def document_parser_exception(self) -> ParseError:
        return self._document_parser_exception


T = TypeVar('T')


class SuiteReadErrorVisitor(ABC, Generic[T]):
    def visit(self, element: SuiteReadError) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(element, SuiteParseError):
            return self.visit_parse_error(element)
        elif isinstance(element, SuiteDoubleInclusion):
            return self.visit_double_inclusion_error(element)
        elif isinstance(element, SuiteFileReferenceError):
            return self.visit_file_reference_error(element)
        else:
            raise TypeError('Unknown {}: {}'.format(SuiteReadError, str(element)))

    @abstractmethod
    def visit_parse_error(self, ex: SuiteParseError) -> T:
        pass

    @abstractmethod
    def visit_double_inclusion_error(self, ex: SuiteDoubleInclusion) -> T:
        pass

    @abstractmethod
    def visit_file_reference_error(self, ex: SuiteFileReferenceError) -> T:
        pass
