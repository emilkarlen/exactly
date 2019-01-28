from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.instructions.assert_ import contents_of_dir
from exactly_lib.instructions.assert_ import define_symbol, change_dir, \
    contents_of_file, env, run, exitcode, new_file, new_dir, \
    shell, existence_of_file, stdout, stderr

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        (instruction_names.EXIT_CODE_INSTRUCTION_NAME, exitcode.setup),
        (instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME, stdout.setup_for_stdout),
        ('stderr', stderr.setup_for_stderr),
        (instruction_names.CONTENTS_OF_EXPLICIT_FILE_INSTRUCTION_NAME, contents_of_file.setup),
        ('exists', existence_of_file.setup),
        (instruction_names.CONTENTS_OF_EXPLICIT_DIR_INSTRUCTION_NAME, contents_of_dir.setup),
        (instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME, define_symbol.setup),
        (instruction_names.CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (instruction_names.NEW_FILE_INSTRUCTION_NAME, new_file.setup),
        (instruction_names.NEW_DIR_INSTRUCTION_NAME, new_dir.setup),
        (instruction_names.ENV_VAR_INSTRUCTION_NAME, env.setup),
        (instruction_names.RUN_INSTRUCTION_NAME, run.setup),
        (instruction_names.SHELL_INSTRUCTION_NAME, shell.setup),
    ]
)
