from typing import List, Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo, InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation


class InstructionParserBase(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self, num_args: int):
        self.num_args = num_args

    def parse_from_source(self, source: ParseSource) -> SetupPhaseInstruction:
        args = source.remaining_part_of_current_line
        source.consume_current_line()
        components = args.split()
        if len(components) != self.num_args:
            raise ValueError('Expecting {} args. Found {} args'.format(self.num_args, len(components)))
        return self._parse(components)

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        raise NotImplementedError('abstract method')


def instruction_setup(setup_phase_instructions: Dict[str, InstructionParser]) -> InstructionsSetup:
    return InstructionsSetup({},
                             {name: SingleInstructionSetup(parser,
                                                           instruction_documentation('name-of-instruction'))
                              for name, parser in setup_phase_instructions.items()},
                             {}, {}, {})
