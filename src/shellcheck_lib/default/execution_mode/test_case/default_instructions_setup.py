from shellcheck_lib.default.execution_mode.test_case.phases import \
    assert_, \
    before_assert, \
    cleanup, \
    configuration, \
    setup
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup

instructions_setup = InstructionsSetup(
        configuration.INSTRUCTIONS,
        setup.INSTRUCTIONS,
        before_assert.INSTRUCTIONS,
        assert_.INSTRUCTIONS,
        cleanup.INSTRUCTIONS)
