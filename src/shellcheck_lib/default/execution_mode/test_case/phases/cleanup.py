from shellcheck_lib.default.execution_mode.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.instructions.cleanup import shell
from shellcheck_lib.instructions.cleanup import change_dir

INSTRUCTIONS = {
    'pwd':
        SingleInstructionSetup(
            change_dir.Parser(),
            change_dir.DESCRIPTION),
    'shell':
        SingleInstructionSetup(
            shell.Parser(),
            shell.DESCRIPTION),

}
