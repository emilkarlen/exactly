from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource


class ParserThatGives(SingleInstructionParser):
    def __init__(self,
                 instruction: Instruction):
        self.instruction = instruction

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        return self.instruction
