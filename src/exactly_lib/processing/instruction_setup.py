from typing import Dict, Optional

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.section_document.element_parsers.parser_for_dictionary_of_instructions import \
    InstructionNameExtractor
from exactly_lib.section_document.section_element_parsing import SectionElementParser


class InstructionsSetup(tuple):
    def __new__(cls,
                config_instruction_set: Optional[Dict[str, SingleInstructionSetup]] = None,
                setup_instruction_set: Optional[Dict[str, SingleInstructionSetup]] = None,
                before_assert_instruction_set: Optional[Dict[str, SingleInstructionSetup]] = None,
                assert_instruction_set: Optional[Dict[str, SingleInstructionSetup]] = None,
                cleanup_instruction_set: Optional[Dict[str, SingleInstructionSetup]] = None,
                ):
        """
        Each SingleInstructionSetup should parse and construct an instruction for
        the correct phase (of course). I.e., sub classes of Instruction.
        """
        return tuple.__new__(cls, (_of(config_instruction_set),
                                   _of(setup_instruction_set),
                                   _of(before_assert_instruction_set),
                                   _of(assert_instruction_set),
                                   _of(cleanup_instruction_set),
                                   ))

    @property
    def config_instruction_set(self) -> Dict[str, SingleInstructionSetup]:
        return self[0]

    @property
    def setup_instruction_set(self) -> Dict[str, SingleInstructionSetup]:
        return self[1]

    @property
    def before_assert_instruction_set(self) -> Dict[str, SingleInstructionSetup]:
        return self[2]

    @property
    def assert_instruction_set(self) -> Dict[str, SingleInstructionSetup]:
        return self[3]

    @property
    def cleanup_instruction_set(self) -> Dict[str, SingleInstructionSetup]:
        return self[4]


class TestCaseParsingSetup:
    def __init__(self,
                 instruction_name_extractor_function: InstructionNameExtractor,
                 instruction_setup: InstructionsSetup,
                 act_phase_parser: SectionElementParser):
        self.instruction_setup = instruction_setup
        self.instruction_name_extractor_function = instruction_name_extractor_function
        self.act_phase_parser = act_phase_parser


def _of(x: Optional[Dict[str, SingleInstructionSetup]]) -> Dict[str, SingleInstructionSetup]:
    return {} if x is None else x
