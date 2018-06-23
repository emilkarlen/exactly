from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.instructions.configuration import home_act, home_case, test_case_status, actor, timeout

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        (instruction_names.HOME_CASE_DIRECTORY_INSTRUCTION_NAME, home_case.setup),
        (instruction_names.HOME_ACT_DIRECTORY_INSTRUCTION_NAME, home_act.setup),
        (instruction_names.TEST_CASE_STATUS_INSTRUCTION_NAME, test_case_status.setup),
        (instruction_names.ACTOR_INSTRUCTION_NAME, actor.setup),
        (instruction_names.TIMEOUT_INSTRUCTION_NAME, timeout.setup),
    ]
)
