from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.default.program_modes.test_case.default_instruction_names import EXECUTION_MODE_INSTRUCTION_NAME, \
    HOME_DIRECTORY_INSTRUCTION_NAME, ACTOR_INSTRUCTION_NAME, TIMEOUT_INSTRUCTION_NAME
from exactly_lib.instructions.configuration import home, execution_mode, actor, timeout

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        (HOME_DIRECTORY_INSTRUCTION_NAME, home.setup),
        (EXECUTION_MODE_INSTRUCTION_NAME, execution_mode.setup),
        (ACTOR_INSTRUCTION_NAME, actor.setup),
        (TIMEOUT_INSTRUCTION_NAME, timeout.setup),
    ]
)
