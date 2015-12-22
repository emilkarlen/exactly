from shellcheck_lib.instructions.assert_phase import change_dir
from shellcheck_lib.instructions.assert_phase import contents as contents_instruction
from shellcheck_lib.instructions.assert_phase import execute
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction
from shellcheck_lib.instructions.assert_phase import new_dir
from shellcheck_lib.instructions.assert_phase import shell
from shellcheck_lib.instructions.assert_phase import stdout_stderr as stdout_stderr_instruction
from shellcheck_lib.instructions.assert_phase import type
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'exitcode':
        SingleInstructionSetup(
                exitcode_instruction.Parser(),
                exitcode_instruction.description('exitcode')),
    'contents':
        SingleInstructionSetup(
                contents_instruction.Parser(),
                contents_instruction.description('contents')),
    'execute':
        SingleInstructionSetup(
                execute.parser('execute'),
                execute.description('execute')),
    'dir':
        SingleInstructionSetup(
                new_dir.Parser(),
                new_dir.description('dir')),
    'pwd':
        SingleInstructionSetup(
                change_dir.Parser(),
                change_dir.description('pwd')),
    'shell':
        SingleInstructionSetup(
                shell.Parser(),
                shell.description('shell')),
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
