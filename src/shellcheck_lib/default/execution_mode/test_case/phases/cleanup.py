from shellcheck_lib.instructions.cleanup import change_dir
from shellcheck_lib.instructions.cleanup import execute
from shellcheck_lib.instructions.cleanup import new_dir
from shellcheck_lib.instructions.cleanup import shell
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'dir':
        SingleInstructionSetup(
                new_dir.Parser(),
                new_dir.description('dir')),
    'execute':
        SingleInstructionSetup(
                execute.parser('execute'),
                execute.description('execute')),
    'shell':
        SingleInstructionSetup(
                shell.Parser(),
                shell.TheDescription('shell')),
    'pwd':
        SingleInstructionSetup(
                change_dir.Parser(),
                change_dir.description('pwd')),
}
