from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.help_texts.test_case.instructions.instruction_names import CHANGE_DIR_INSTRUCTION_NAME, \
    SHELL_INSTRUCTION_NAME
from exactly_lib.instructions.assert_ import change_dir, \
    contents_of_dir, contents_of_file, env, run, exitcode, new_dir, \
    shell, existence_of_file, stdout, stderr

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('contents', contents_of_file.setup),
        ('dir-contents', contents_of_dir.setup),
        ('dir', new_dir.setup),
        ('env', env.setup),
        ('run', run.setup),
        ('exitcode', exitcode.setup),
        (CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (SHELL_INSTRUCTION_NAME, shell.setup),
        ('stderr', stderr.setup_for_stderr),
        ('stdout', stdout.setup_for_stdout),
        ('exists', existence_of_file.setup),
    ]
)
