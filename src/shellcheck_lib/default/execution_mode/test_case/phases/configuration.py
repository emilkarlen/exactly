from shellcheck_lib.instructions.configuration import home, execution_mode
from shellcheck_lib.test_case.instruction_setup import instruction_set_from_name_and_setup_constructor_list

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
        [
            ('home', home.setup),
            ('mode', execution_mode.setup),
        ]
)
