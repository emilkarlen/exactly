import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert.utils import instruction_from_parts as sut
from exactly_lib.instructions.multi_phase_instructions.utils.parser import InstructionPartsParser
from exactly_lib.instructions.utils.instruction_parts import InstructionParts
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import instruction_from_parts as tr


def suite() -> unittest.TestSuite:
    return tr.suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase, tr.Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        raise NotImplementedError('this method should not be used')

    def new_instruction_from_parts(self, parts: InstructionParts):
        return sut.BeforeAssertPhaseInstructionFromValidatorAndExecutor(parts)

    def step_sequence_of_successful_execution(self) -> list:
        return [
            tr.VALIDATE_STEP_PRE_SDS_IF_APPLICABLE,
            tr.VALIDATE_STEP_POST_SDS_IF_APPLICABLE,
            tr.MAIN_STEP_AS_NON_ASSERTION,
        ]

    def instruction_parser_from_parts_parser(self, parts_parser: InstructionPartsParser
                                             ) -> InstructionParser:
        return sut.Parser(parts_parser)
