from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.configuration import act_home, home, test_case_status, actor, timeout

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        (instruction_names.HOME_CASE_DIRECTORY_INSTRUCTION_NAME, home.setup),
        (instruction_names.HOME_ACT_DIRECTORY_INSTRUCTION_NAME, act_home.setup),
        (instruction_names.TEST_CASE_STATUS_INSTRUCTION_NAME, test_case_status.setup),
        (instruction_names.ACTOR_INSTRUCTION_NAME, actor.setup),
        (instruction_names.TIMEOUT_INSTRUCTION_NAME, timeout.setup),
    ]
)
