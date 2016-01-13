from shellcheck_lib.instructions.before_assert import change_dir, env, execute, shell, new_dir
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'dir':
        SingleInstructionSetup(
                new_dir.Parser(),
                new_dir.description('dir')),
    'env':
        SingleInstructionSetup(
                env.PARSER,
                env.description('env')),
    'execute':
        SingleInstructionSetup(
                execute.parser('execute'),
                execute.description('execute')),
    'pwd':
        SingleInstructionSetup(
                change_dir.Parser(),
                change_dir.description('pwd')),
    'shell':
        SingleInstructionSetup(
                shell.parser('shell'),
                shell.description('shell')),
}
