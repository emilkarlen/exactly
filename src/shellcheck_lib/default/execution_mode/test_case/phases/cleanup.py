from shellcheck_lib.default.execution_mode.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.instructions.cleanup import shell as cleanup_shell

INSTRUCTIONS = {
    'shell':
        SingleInstructionSetup(
            cleanup_shell.Parser(),
            cleanup_shell.DESCRIPTION),

}
