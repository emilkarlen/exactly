from shellcheck_lib.default.execution_mode.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.instructions.assert_phase import shell as assert_shell
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction
from shellcheck_lib.instructions.assert_phase import contents as contents_instruction
from shellcheck_lib.instructions.assert_phase import type
from shellcheck_lib.instructions.assert_phase import stdout_stderr as stdout_stderr_instruction

INSTRUCTIONS = {
    'exitcode':
        SingleInstructionSetup(
            exitcode_instruction.Parser(),
            exitcode_instruction.DESCRIPTION),
    'contents':
        SingleInstructionSetup(
            contents_instruction.Parser(),
            contents_instruction.DESCRIPTION),
    'shell':
        SingleInstructionSetup(
            assert_shell.Parser(),
            assert_shell.DESCRIPTION),
    'stdout':
        SingleInstructionSetup(
            stdout_stderr_instruction.ParserForContentsForStdout(),
            stdout_stderr_instruction.description('stdout')),
    'stderr':
        SingleInstructionSetup(
            stdout_stderr_instruction.ParserForContentsForStderr(),
            stdout_stderr_instruction.description('stderr')),
    'type':
        SingleInstructionSetup(
            type.Parser(),
            type.DESCRIPTION),
}
