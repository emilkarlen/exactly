import pathlib

from shellcheck_lib.util import line_source


class SuiteReadError(Exception):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line):
        self._suite_file = suite_file
        self._line = line

    @property
    def suite_file(self) -> pathlib.Path:
        return self._suite_file

    @property
    def line(self) -> line_source.Line:
        return self._line


class SuiteDoubleInclusion(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 included_suite_file: pathlib.Path,
                 first_referenced_from: pathlib.Path):
        super().__init__(suite_file, line)
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


class SuiteFileReferenceError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 reference: pathlib.Path):
        super().__init__(suite_file, line)
        self._reference = reference

    @property
    def reference(self) -> pathlib.Path:
        return self._reference


class SuiteSyntaxError(SuiteReadError):
    def __init__(self,
                 suite_file: pathlib.Path,
                 line: line_source.Line,
                 message: str,
                 maybe_section_name: str = None):
        super().__init__(suite_file, line)
        self._message = message
        self._maybe_section_name = maybe_section_name

    @property
    def message(self) -> str:
        return self._message

    @property
    def maybe_section_name(self) -> str:
        return self._maybe_section_name
