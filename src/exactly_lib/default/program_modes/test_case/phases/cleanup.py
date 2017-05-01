from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.help_texts.test_case.instructions.instruction_names import CHANGE_DIR_INSTRUCTION_NAME, \
    SHELL_INSTRUCTION_NAME
from exactly_lib.instructions.cleanup import change_dir, env, run, new_dir, shell

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('dir', new_dir.setup),
        ('env', env.setup),
        ('run', run.setup),
        (CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (SHELL_INSTRUCTION_NAME, shell.setup),
    ]
)
