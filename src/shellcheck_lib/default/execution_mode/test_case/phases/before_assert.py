from shellcheck_lib.instructions.cleanup import execute, shell
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'execute':
        SingleInstructionSetup(
                execute.parser('execute'),
                execute.description('execute')),
    'shell':
        SingleInstructionSetup(
                shell.parser(),
                shell.description('shell')),
}
