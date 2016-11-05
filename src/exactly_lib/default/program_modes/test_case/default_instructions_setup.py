from exactly_lib.default.program_modes.test_case.phases import \
    assert_, \
    before_assert, \
    cleanup, \
    configuration, \
    setup
from exactly_lib.processing.instruction_setup import InstructionsSetup

INSTRUCTIONS_SETUP = InstructionsSetup(
    configuration.INSTRUCTIONS,
    setup.INSTRUCTIONS,
    before_assert.INSTRUCTIONS,
    assert_.INSTRUCTIONS,
    cleanup.INSTRUCTIONS)
