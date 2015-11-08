from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.default.execution_mode.test_case.phases import configuration
from shellcheck_lib.default.execution_mode.test_case.phases import setup
from shellcheck_lib.default.execution_mode.test_case.phases import assert_
from shellcheck_lib.default.execution_mode.test_case.phases import cleanup

instructions_setup = InstructionsSetup(
    configuration.INSTRUCTIONS,
    setup.INSTRUCTIONS,
    assert_.INSTRUCTIONS,
    cleanup.INSTRUCTIONS)
