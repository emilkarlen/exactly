import io
import pathlib
import shlex

from exactly_lib.section_document import syntax
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParser, InstructionAndDescriptionParser, parse_and_compute_source
from exactly_lib.section_document.exceptions import new_source_error_of_single_line
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parser import ParsedInstruction
from exactly_lib.util.line_source import Line


class InstructionWithOptionalDescriptionParser(InstructionAndDescriptionParser):
    def __init__(self, instruction_parser: InstructionParser):
        self.instruction_parser = instruction_parser

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedInstruction:
        first_line = source.current_line
        description = _DescriptionExtractor(source).apply()
        self._consume_space_and_comment_lines(source, first_line)
        return parse_and_compute_source(self.instruction_parser, source, description)

    @staticmethod
    def _consume_space_and_comment_lines(source: ParseSource, first_line: Line):
        error_message = 'End-of-file reached without finding an instruction (following a description)'
        if source.is_at_eof:
            raise new_source_error_of_single_line(first_line, error_message)
        line_in_error_message = first_line
        source.consume_initial_space_on_current_line()
        if not source.is_at_eol:
            return
        source.consume_current_line()
        while not source.is_at_eof:
            if syntax.is_empty_or_comment_line(source.current_line_text):
                line_in_error_message = source.current_line
                source.consume_current_line()
            else:
                source.consume_initial_space_on_current_line()
                return
        raise new_source_error_of_single_line(line_in_error_message, error_message)


class _DescriptionExtractor:
    def __init__(self, source: ParseSource):
        self.source = source
        self.source.consume_initial_space_on_current_line()
        self.source_io = io.StringIO(source.remaining_source)
        self.lexer = shlex.shlex(self.source_io, posix=True)

    def apply(self) -> str:
        ret_val = None
        if self.starts_with_description():
            ret_val = self.extract_and_consume_description()
        return ret_val

    def extract_and_consume_description(self) -> str:
        try:
            string_token = self.lexer.get_token()
        except ValueError as ex:
            raise new_source_error_of_single_line(self.source.current_line,
                                                  'Invalid description: ' + str(ex))
        num_chars_consumed = self.source_io.tell()
        if len(self.source.remaining_source) > num_chars_consumed:
            num_chars_consumed -= 1
        self.source.consume(num_chars_consumed)
        return string_token.strip()

    def starts_with_description(self) -> bool:
        stripped_first_line = self.source.remaining_part_of_current_line
        return stripped_first_line and stripped_first_line[0] in self.lexer.quotes
