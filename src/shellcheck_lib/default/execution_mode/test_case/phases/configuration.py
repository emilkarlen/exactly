from shellcheck_lib.instructions.configuration import home, execution_mode
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'home':
        SingleInstructionSetup(
                home.Parser(),
                home.TheDescription('home')),
    'mode':
        SingleInstructionSetup(
                execution_mode.Parser(),
                execution_mode.TheDescription('mode')),
}
