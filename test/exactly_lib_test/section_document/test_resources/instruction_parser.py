from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionParser


class ParserThatGives(InstructionParser):
    def __init__(self,
                 instruction: Instruction):
        self.instruction = instruction

    def parse(self, source: ParseSource) -> Instruction:
        source.consume_current_line()
        return self.instruction
