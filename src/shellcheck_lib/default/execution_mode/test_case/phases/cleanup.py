from shellcheck_lib.instructions.cleanup import change_dir
from shellcheck_lib.instructions.cleanup import execute
from shellcheck_lib.instructions.cleanup import new_dir
from shellcheck_lib.instructions.cleanup import shell
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'dir':
        SingleInstructionSetup(
            new_dir.Parser(),
            new_dir.DESCRIPTION),
    'execute':
        SingleInstructionSetup(
            execute.parser('execute'),
            execute.DESCRIPTION),
    'shell':
        SingleInstructionSetup(
            shell.Parser(),
            shell.DESCRIPTION),
    'pwd':
        SingleInstructionSetup(
            change_dir.Parser(),
            change_dir.DESCRIPTION),

}
