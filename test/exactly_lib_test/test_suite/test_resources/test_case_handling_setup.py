from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.cli.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR


def test_case_handling_setup_with_identity_preprocessor() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(single_command_setup.act_phase_setup(),
                                 IDENTITY_PREPROCESSOR)
