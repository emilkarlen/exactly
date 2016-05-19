from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


def test_case_handling_setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(single_command_setup.act_phase_setup(),
                                 IdentityPreprocessor())
