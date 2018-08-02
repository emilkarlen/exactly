from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo


class InstructionParserThatConsumesCurrentLine(InstructionParser):
    """
    A parser that unconditionally consumes the current line,
    and that uses the remaining part of the current line for
    constructing the parsed instruction.

    The parser cannot consume any more than the current line.

    Precondition: The source must have a current line.
    """

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        rest_of_line = source.remaining_part_of_current_line
        source.consume_current_line()
        return self._parse(rest_of_line)

    def _parse(self, rest_of_line: str) -> model.Instruction:
        raise NotImplementedError()
