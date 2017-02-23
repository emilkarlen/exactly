from exactly_lib.util import line_source


class SourceError(Exception):
    """
    An exceptions related to a line in the test case,
    raised by a parser that is unaware of current section.
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
    def message(self) -> str:
        return self._message


class FileSourceError(Exception):
    """
    An exceptions related to a line in the test case.
    """

    def __init__(self,
                 source_error: SourceError,
                 maybe_section_name: str):
        self._source_error = source_error
        self._maybe_section_name = maybe_section_name

    @property
    def source_error(self) -> SourceError:
        return self._source_error

    @property
    def maybe_section_name(self) -> str:
        return self._maybe_section_name
