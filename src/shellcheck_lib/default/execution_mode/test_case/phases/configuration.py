from shellcheck_lib.instructions.configuration import home
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup

INSTRUCTIONS = {
    'home':
        SingleInstructionSetup(
                home.Parser(),
                home.TheDescription('home')),
}
