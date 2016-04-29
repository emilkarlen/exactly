from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.instructions.assert_ import change_dir, contents, env, execute, exitcode, new_dir, \
    shell, stdout_stderr, type
from exactly_lib.test_case.instruction_setup import instruction_set_from_name_and_setup_constructor_list

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
    [
        ('contents', contents.setup),
        ('dir', new_dir.setup),
        ('env', env.setup),
        ('run', execute.setup),
        ('exitcode', exitcode.setup),
        (CHANGE_DIR_INSTRUCTION_NAME, change_dir.setup),
        ('shell', shell.setup),
        ('stderr', stdout_stderr.setup_for_stderr),
        ('stdout', stdout_stderr.setup_for_stdout),
        ('type', type.setup),
    ]
)
