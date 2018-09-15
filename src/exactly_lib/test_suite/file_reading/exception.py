import pathlib
from typing import List, Optional

from exactly_lib.definitions.test_suite import section_names_plain
from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath
from exactly_lib.test_case import error_description
from exactly_lib.util import line_source


class SuiteReadError(Exception):
    def __init__(self,
                 suite_file: pathlib.Path,
                 source: line_source.LineSequence,
                 maybe_section_name: Optional[str] = None):
        self._suite_file = suite_file
        self._source = source
        self._maybe_section_name = maybe_section_name

    @property
    def suite_file(self) -> pathlib.Path:
        return self._suite_file

    @property
    def source(self) -> line_source.LineSequence:
        return self._source

    @property
    def source_location(self) -> SourceLocationPath:
        return SourceLocationPath(SourceLocation(self.source,
                                                 self.suite_file),
                                  [])

    @property
    def maybe_section_name(self) -> Optional[str]:
        return self._maybe_section_name

    def error_message_lines(self) -> List[str]:
        """
        Error message text that are specific for the exception class.
        """
        raise NotImplementedError()


class SuiteDoubleInclusion(SuiteReadError):
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

    def error_message_lines(self) -> List[str]:
        return ['The suite has already been included.']


class SuiteFileReferenceError(SuiteReadError):
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

    def error_message_lines(self) -> List[str]:
        return [
            self.error_message_header + ':',
            str(self.reference)
        ]


class SuiteSyntaxError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 source: line_source.LineSequence,
                 message: str,
                 maybe_section_name: Optional[str] = None):
        super().__init__(suite_file,
                         source,
                         maybe_section_name)
        self._message = message

    def error_message_lines(self) -> List[str]:
        return [error_description.syntax_error_message(self._message)]
