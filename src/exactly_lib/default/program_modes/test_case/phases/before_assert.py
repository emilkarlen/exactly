from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.before_assert import change_dir, env, run, shell, new_dir, transform

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('dir', new_dir.setup),
        ('env', env.setup),
        (instruction_names.RUN_INSTRUCTION_NAME, run.setup),
        (instruction_names.CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (instruction_names.SHELL_INSTRUCTION_NAME, shell.setup),
        (instruction_names.TRANSFORM_FILE_INSTRUCTION_NAME, transform.setup),
    ]
)
