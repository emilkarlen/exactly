import pathlib

from exactly_lib.test_case import error_description
from exactly_lib.util import line_source


class SuiteReadError(Exception):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 maybe_section_name: str = None):
        self._suite_file = suite_file
        self._line = line
        self._maybe_section_name = maybe_section_name

    @property
    def suite_file(self) -> pathlib.Path:
        return self._suite_file

    @property
    def line(self) -> line_source.Line:
        return self._line

    @property
    def maybe_section_name(self) -> str:
        """
        :return: str?
        """
        return self._maybe_section_name

    def error_message_lines(self) -> list:
        """
        Error message text that are specific for the exception class.
        """
        raise NotImplementedError()


class SuiteDoubleInclusion(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 included_suite_file: pathlib.Path,
                 first_referenced_from: pathlib.Path):
        super().__init__(suite_file, line, None)
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

    def error_message_lines(self) -> list:
        return ['The suite has already been included.']


class SuiteFileReferenceError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 reference: pathlib.Path):
        super().__init__(suite_file, line, None)
        self._reference = reference

    @property
    def reference(self) -> pathlib.Path:
        return self._reference

    def error_message_lines(self) -> list:
        return [
            'Cannot access file:',
            str(self.reference)
        ]


class SuiteSyntaxError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 message: str,
                 maybe_section_name: str = None):
        super().__init__(suite_file, line, maybe_section_name)
        self._message = message

    def error_message_lines(self) -> list:
        return [error_description.syntax_error_message(self._message)]
