from exactly_lib.common.instruction_setup import instruction_set_from_name_and_setup_constructor_list
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME, \
    SHELL_INSTRUCTION_NAME
from exactly_lib.instructions.assert_ import change_dir, contents, env, run, exitcode, new_dir, \
    shell, type, stdout, stderr

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('contents', contents.setup),
        ('dir', new_dir.setup),
        ('env', env.setup),
        ('run', run.setup),
        ('exitcode', exitcode.setup),
        (CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        (SHELL_INSTRUCTION_NAME, shell.setup),
        ('stderr', stderr.setup_for_stderr),
        ('stdout', stdout.setup_for_stdout),
        ('type', type.setup),
    ]
)
