from shellcheck_lib.instructions.assert_phase import change_dir
from shellcheck_lib.instructions.assert_phase import contents as contents_instruction
from shellcheck_lib.instructions.assert_phase import env
from shellcheck_lib.instructions.assert_phase import execute
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction
from shellcheck_lib.instructions.assert_phase import new_dir
from shellcheck_lib.instructions.assert_phase import shell
from shellcheck_lib.instructions.assert_phase import stdout_stderr as stdout_stderr_instruction
from shellcheck_lib.instructions.assert_phase import type
from shellcheck_lib.test_case.instruction_setup import instruction_set_from_name_and_setup_constructor_list

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
        [
            ('contents', contents_instruction.setup),
            ('dir', new_dir.setup),
            ('env', env.setup),
            ('execute', execute.setup),
            ('exitcode', exitcode_instruction.setup),
            ('pwd', change_dir.setup),
            ('shell', shell.setup),
            ('stderr', stdout_stderr_instruction.setup_for_stderr),
            ('stdout', stdout_stderr_instruction.setup_for_stdout),
            ('type', type.setup),
        ]
)
