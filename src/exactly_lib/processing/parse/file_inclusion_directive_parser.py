import pathlib

from exactly_lib.section_document.document_parser import SectionElementParser
from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parser import ParsedFileInclusionDirective
from exactly_lib.util.line_source import line_sequence_from_line


class FileInclusionDirectiveParser(SectionElementParser):
    """
    Element parser that parses a :class:`ParsedFileInclusionDirective`

    Syntax:

      DIRECTIVE_NAME PATH

    PATH uses Posix syntax

    DIRECTIVE_NAME is a string given to the constructor, that must not contain space.


    The parser returns None iff the source is not a line that starts with DIRECTIVE_NAME
    """

    def __init__(self, directive_token: str):
        """
        :param directive_token: The directive token that precedes the path. Must not contain space.
        """
        self._directive_token = directive_token

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedFileInclusionDirective:
        parts = source.current_line_text.strip().split()
        if len(parts) == 0 or parts[0] != self._directive_token:
            return None
        directive_source = line_sequence_from_line(source.current_line)
        source.consume_current_line()
        if len(parts) == 1:
            raise SourceError(directive_source,
                              'Missing FILE argument')

        if len(parts) != 2:
            raise SourceError(directive_source,
                              'Superfluous arguments: ' + ' '.join(parts[2:]))

        path = pathlib.Path(pathlib.PurePosixPath(parts[1]))
        return ParsedFileInclusionDirective(directive_source,
                                            [path])
