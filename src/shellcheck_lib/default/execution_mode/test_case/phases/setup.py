from shellcheck_lib.default.execution_mode.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.instructions.setup import env
from shellcheck_lib.instructions.setup import install
from shellcheck_lib.instructions.setup import shell
from shellcheck_lib.instructions.setup import mkdir
from shellcheck_lib.instructions.setup import change_dir
from shellcheck_lib.instructions.setup import stdin

INSTRUCTIONS = {
    'env':
        SingleInstructionSetup(
            env.Parser(),
            env.DESCRIPTION),
    'install':
        SingleInstructionSetup(
            install.Parser(),
            install.DESCRIPTION),
    'mkdir':
        SingleInstructionSetup(
            mkdir.Parser(),
            mkdir.DESCRIPTION),
    'pwd':
        SingleInstructionSetup(
            change_dir.Parser(),
            change_dir.DESCRIPTION),
    'shell':
        SingleInstructionSetup(
            shell.Parser(),
            shell.DESCRIPTION),
    'stdin':
        SingleInstructionSetup(
            stdin.Parser(),
            stdin.DESCRIPTION),
}
