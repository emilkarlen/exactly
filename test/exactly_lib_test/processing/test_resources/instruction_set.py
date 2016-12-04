from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document.model import Instruction
from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.execution.test_resources import instruction_test_resources as instr


def instruction_set() -> InstructionsSetup:
    return InstructionsSetup(
        config_instruction_set=dict(
            [instruction_item('conf_instruction',
                              instr.configuration_phase_instruction_that())]),
        setup_instruction_set=dict(
            [instruction_item('setup_instruction',
                              instr.setup_phase_instruction_that())]),
        assert_instruction_set=dict(
            [instruction_item('assert_instruction',
                              instr.assert_phase_instruction_that())]),
        before_assert_instruction_set=dict(
            [instruction_item('before_assert_instruction',
                              instr.before_assert_phase_instruction_that())]),
        cleanup_instruction_set=dict(
            [instruction_item('cleanup_instruction',
                              instr.cleanup_phase_instruction_that())]),
    )


def instruction_item(instruction_name: str,
                     instruction: Instruction) -> (str, SingleInstructionSetup):
    return (instruction_name,
            single_instruction_setup(instruction_name,
                                     instruction))
