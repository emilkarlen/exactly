from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.instructions.setup import change_dir, env, run, copy, new_dir, new_file, shell, stdin, \
    define_symbol

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('stdin', stdin.setup),
        ('copy', copy.setup),
        (instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME, define_symbol.setup),
        (instruction_names.CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (instruction_names.ENV_VAR_INSTRUCTION_NAME, env.setup),
        (instruction_names.NEW_FILE_INSTRUCTION_NAME, new_file.setup),
        (instruction_names.NEW_DIR_INSTRUCTION_NAME, new_dir.setup),
        (instruction_names.RUN_INSTRUCTION_NAME, run.setup),
        (instruction_names.SHELL_INSTRUCTION_NAME, shell.setup),
    ]
)
