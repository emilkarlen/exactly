from exactly_lib.common.instruction_documentation import InstructionDocumentation
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource


class SingleInstructionSetup(SingleInstructionParser):
    def __init__(self,
                 parser: SingleInstructionParser,
                 description: InstructionDocumentation):
        self._parser = parser
        self._description = description

    @property
    def description(self) -> InstructionDocumentation:
        return self._description

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        return self._parser.apply(source)


def instruction_set_from_name_and_setup_constructor_list(name_and_setup_pair_list: list) -> dict:
    return dict(map(_name_and_setup, name_and_setup_pair_list))


def _name_and_setup(instruction_name__and__setup_constructor) -> (str, SingleInstructionSetup):
    instruction_name = instruction_name__and__setup_constructor[0]
    setup_constructor = instruction_name__and__setup_constructor[1]
    return (instruction_name,
            setup_constructor(instruction_name))
