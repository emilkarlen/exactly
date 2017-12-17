from typing import Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup


class InstructionsSetup(tuple):
    def __new__(cls,
                config_instruction_set: Dict[str, SingleInstructionSetup],
                setup_instruction_set: Dict[str, SingleInstructionSetup],
                before_assert_instruction_set: Dict[str, SingleInstructionSetup],
                assert_instruction_set: Dict[str, SingleInstructionSetup],
                cleanup_instruction_set: Dict[str, SingleInstructionSetup]):
        """
        Each SingleInstructionSetup should parse and construct an instruction for
        the correct phase (of course). I.e., sub classes of Instruction.
        """
        return tuple.__new__(cls, (config_instruction_set,
                                   setup_instruction_set,
                                   before_assert_instruction_set,
                                   assert_instruction_set,
                                   cleanup_instruction_set))

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
