from exactly_lib.instructions.utils.instruction_parts import InstructionParts
from exactly_lib.section_document.parse_source import ParseSource


class InstructionPartsParser:
    """
    Parser of `InstructionParts` - used by instructions that may be used in multiple phases. 
    """

    def parse(self, source: ParseSource) -> InstructionParts:
        raise NotImplementedError()


class InstructionPartsParserThatConsumesCurrentLine(InstructionPartsParser):
    """
    A parser that unconditionally consumes the current line,
    and that uses the remaining part of the current line for
    constructing the parsed instruction.

    The parser cannot consume any more than the current line.

    Precondition: The source must have a current line.
    """

    def parse(self, source: ParseSource) -> InstructionParts:
        rest_of_line = source.remaining_part_of_current_line
        source.consume_current_line()
        return self._parse(rest_of_line)

    def _parse(self, rest_of_line: str) -> InstructionParts:
        raise NotImplementedError()
