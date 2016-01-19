from shellcheck_lib.instructions.assert_phase import change_dir, contents, env, execute, exitcode, new_dir, \
    shell, stdout_stderr, type
from shellcheck_lib.test_case.instruction_setup import instruction_set_from_name_and_setup_constructor_list

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
        [
            ('contents', contents.setup),
            ('dir', new_dir.setup),
            ('env', env.setup),
            ('execute', execute.setup),
            ('exitcode', exitcode.setup),
            ('pwd', change_dir.setup),
            ('shell', shell.setup),
            ('stderr', stdout_stderr.setup_for_stderr),
            ('stdout', stdout_stderr.setup_for_stdout),
            ('type', type.setup),
        ]
)
