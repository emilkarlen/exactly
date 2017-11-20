from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.assert_ import change_dir, \
    contents_of_file, env, run, exitcode, new_dir, \
    shell, existence_of_file, stdout, stderr, transform
from exactly_lib.instructions.assert_ import contents_of_dir

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('contents', contents_of_file.setup),
        ('dir-contents', contents_of_dir.setup),
        ('dir', new_dir.setup),
        ('env', env.setup),
        (instruction_names.RUN_INSTRUCTION_NAME, run.setup),
        ('exitcode', exitcode.setup),
        (instruction_names.CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (instruction_names.SHELL_INSTRUCTION_NAME, shell.setup),
        ('stderr', stderr.setup_for_stderr),
        (instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME, stdout.setup_for_stdout),
        ('exists', existence_of_file.setup),
        (instruction_names.TRANSFORM_FILE_INSTRUCTION_NAME, transform.setup),
    ]
)
