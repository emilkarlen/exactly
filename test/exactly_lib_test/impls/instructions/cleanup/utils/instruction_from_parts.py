import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.cleanup.utils import instruction_from_parts as sut
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionParts, \
    InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib_test.impls.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources import \
    instruction_from_parts as tr


def suite() -> unittest.TestSuite:
    return tr.suite_for(TheConfiguration())


class TheConfiguration(CleanupConfigurationBase, tr.Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        raise NotImplementedError('this method should not be used')

    def new_instruction_from_parts(self, parts: InstructionParts):
        return sut.CleanupPhaseInstructionFromParts(parts)

    def step_sequence_of_successful_execution(self) -> list:
        return [
            tr.VALIDATE_STEP_PRE_SDS_IF_APPLICABLE,
            tr.VALIDATE_STEP_POST_SETUP_IF_APPLICABLE,
            tr.MAIN_STEP_AS_NON_ASSERTION,
        ]

    def instruction_parser_from_parts_parser(self, parts_parser: InstructionPartsParser
                                             ) -> InstructionParser:
        return sut.Parser(parts_parser)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
