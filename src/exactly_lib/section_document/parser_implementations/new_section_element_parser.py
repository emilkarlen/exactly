from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.new_parser_classes import ElementParser2
from exactly_lib.util import line_source


class InstructionParser2:
    def parse(self, source: ParseSource) -> model.Instruction:
        """
        :raises FileSourceError The instruction cannot be parsed.
        """
        raise NotImplementedError()


class StandardSyntaxElementParser(ElementParser2):
    """
    A parser that knows how to parse empty lines and
    comment lines (denoted by standard syntax).
    Every other line is treated as the start of an
    instruction to be parsed by a given instruction parser.
    """

    def __init__(self, instruction_parser: InstructionParser2):
        self.instruction_parser = instruction_parser

    def parse(self, source: ParseSource) -> model.SectionContentElement:
        first_line = source.current_line
        if syntax.is_empty_line(first_line.text):
            return model.new_empty_e(self._consume_and_return_current_line(source))
        if syntax.is_comment_line(first_line.text):
            return model.new_comment_e(self._consume_and_return_current_line(source))
        else:
            source_before = source.remaining_source
            first_line_number = source.current_line_number
            len_before_parse = len(source_before)
            instruction = self.instruction_parser.parse(source)
            len_after_parse = len(source.remaining_source)
            len_instruction_source = len_before_parse - len_after_parse
            instruction_source = source_before[:len_instruction_source]
            return model.new_instruction_e(line_source.LineSequence(first_line_number,
                                                                    tuple(instruction_source.split('\n'))),
                                           instruction)

    @staticmethod
    def _consume_and_return_current_line(source: ParseSource) -> line_source.LineSequence:
        current_line = source.current_line
        source.consume_current_line()
        return line_source.LineSequence(current_line.line_number,
                                        (current_line.text,))
