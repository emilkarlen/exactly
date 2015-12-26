from shellcheck_lib.instructions.setup import change_dir
from shellcheck_lib.instructions.setup import env
from shellcheck_lib.instructions.setup import execute
from shellcheck_lib.instructions.setup import install
from shellcheck_lib.instructions.setup import new_dir
from shellcheck_lib.instructions.setup import new_file
from shellcheck_lib.instructions.setup import shell
from shellcheck_lib.instructions.setup import stdin
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'env':
        SingleInstructionSetup(
                env.Parser(),
                env.TheDescription('env')),
    'execute':
        SingleInstructionSetup(
                execute.parser('execute'),
                execute.description('execute')),
    'file':
        SingleInstructionSetup(
                new_file.Parser(),
                new_file.description('file')),
    'install':
        SingleInstructionSetup(
                install.Parser(),
                install.TheDescription('install')),
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
                shell.parser(),
                shell.TheDescription('shell')),
    'stdin':
        SingleInstructionSetup(
                stdin.Parser(),
                stdin.TheDescription('stdin')),
}
