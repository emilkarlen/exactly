from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME, \
    SHELL_INSTRUCTION_NAME, SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.instructions.setup import change_dir, env, run, install, new_dir, new_file, shell, stdin, \
    assign_symbol

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('dir', new_dir.setup),
        ('env', env.setup),
        ('run', run.setup),
        ('file', new_file.setup),
        ('install', install.setup),
        (CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (SHELL_INSTRUCTION_NAME, shell.setup),
        ('stdin', stdin.setup),
        (SYMBOL_DEFINITION_INSTRUCTION_NAME, assign_symbol.setup),
    ]
)
