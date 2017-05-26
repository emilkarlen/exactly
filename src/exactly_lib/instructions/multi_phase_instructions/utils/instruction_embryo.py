from exactly_lib.section_document.parse_source import ParseSource


class InstructionEmbryo:
    @property
    def symbol_usages(self) -> list:
        return []


class InstructionEmbryoParser:
    def parse(self, source: ParseSource) -> InstructionEmbryo:
        raise NotImplementedError()


class InstructionEmbryoParserThatConsumesCurrentLine(InstructionEmbryoParser):
    """
    A parser that unconditionally consumes the current line,
    and that uses the remaining part of the current line for
    constructing the parsed instruction.

    The parser cannot consume any more than the current line.

    Precondition: The source must have a current line.
    """

    def parse(self, source: ParseSource) -> InstructionEmbryo:
        rest_of_line = source.remaining_part_of_current_line
        source.consume_current_line()
        return self._parse(rest_of_line)

    def _parse(self, rest_of_line: str) -> InstructionEmbryo:
        raise NotImplementedError()
