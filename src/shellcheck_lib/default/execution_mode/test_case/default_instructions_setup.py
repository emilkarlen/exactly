from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup, \
    SingleInstructionSetup
from shellcheck_lib.instructions.configuration import home
from shellcheck_lib.instructions.setup import env
from shellcheck_lib.instructions.setup import install
from shellcheck_lib.instructions.setup import shell as setup_shell
from shellcheck_lib.instructions.cleanup import shell as cleanup_shell
from shellcheck_lib.instructions.assert_phase import shell as assert_shell
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction
from shellcheck_lib.instructions.assert_phase import contents as contents_instruction
from shellcheck_lib.instructions.assert_phase import type
from shellcheck_lib.instructions.assert_phase import stdout_stderr as stdout_stderr_instruction

instructions_setup = InstructionsSetup(
    {
        'home':
            SingleInstructionSetup(
                home.Parser(),
                home.DESCRIPTION),
    },
    {
        'env':
            SingleInstructionSetup(
                env.Parser(),
                env.DESCRIPTION),
        'install':
            SingleInstructionSetup(
                install.Parser(),
                install.DESCRIPTION),
        'shell':
            SingleInstructionSetup(
                setup_shell.Parser(),
                setup_shell.DESCRIPTION),
    },
    {
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
    },
    {
        'shell':
            SingleInstructionSetup(
                cleanup_shell.Parser(),
                cleanup_shell.DESCRIPTION),

    })
