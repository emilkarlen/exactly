import io
import shlex

from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parse import SourceError
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionAndDescription, \
    InstructionParser, InstructionAndDescriptionParser


class InstructionWithOptionalDescriptionParser(InstructionAndDescriptionParser):
    def __init__(self, instruction_parser: InstructionParser):
        self.instruction_parser = instruction_parser

    def parse(self, source: ParseSource) -> InstructionAndDescription:
        description = _DescriptionExtractor(source).apply()
        source.consume_initial_space_on_current_line()
        instruction = self.instruction_parser.parse(source)
        return InstructionAndDescription(instruction, description)


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
            raise SourceError(self.source.current_line,
                              'Invalid description: ' + str(ex))
        num_chars_consumed = self.source_io.tell() - 1
        self.source.consume(num_chars_consumed)
        if self.source.is_at_eol:
            self.source.consume_current_line()
        return string_token.strip()

    def starts_with_description(self) -> bool:
        stripped_first_line = self.source.remaining_part_of_current_line
        return stripped_first_line and stripped_first_line[0] in self.lexer.quotes
