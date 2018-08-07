from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource


class ParserThatGives(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self, instruction: Instruction):
        self.instruction = instruction

    def parse_from_source(self, source: ParseSource) -> Instruction:
        source.consume_current_line()
        return self.instruction
