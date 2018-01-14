from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource


class SingleInstructionSetup(InstructionParser):
    def __init__(self,
                 parser: InstructionParser,
                 documentation: InstructionDocumentation):
        self._parser = parser
        self._documentation = documentation

    @property
    def documentation(self) -> InstructionDocumentation:
        return self._documentation

    def parse(self, source: ParseSource) -> Instruction:
        return self._parser.parse(source)


def instruction_set_from_name_and_setup_constructor_list(name_and_setup_pair_list: list) -> dict:
    return dict(map(_name_and_setup, name_and_setup_pair_list))


def _name_and_setup(instruction_name__and__setup_constructor) -> (str, SingleInstructionSetup):
    instruction_name = instruction_name__and__setup_constructor[0]
    setup_constructor = instruction_name__and__setup_constructor[1]
    return (instruction_name,
            setup_constructor(instruction_name))
