from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import change_dir as cd_utils


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(cd_utils.parts_parser(is_after_act_phase=True)),
        cd_utils.TheInstructionDocumentation(instruction_name,
                                             is_after_act_phase=True,
                                             is_in_assert_phase=False))
