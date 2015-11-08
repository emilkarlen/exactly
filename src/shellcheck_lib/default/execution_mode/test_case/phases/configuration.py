from shellcheck_lib.default.execution_mode.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.instructions.configuration import home

INSTRUCTIONS = {
    'home':
        SingleInstructionSetup(
            home.Parser(),
            home.DESCRIPTION),
}
