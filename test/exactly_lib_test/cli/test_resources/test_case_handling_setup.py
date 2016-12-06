from exactly_lib.act_phase_setups import command_line
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


def test_case_handling_setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(command_line.act_phase_setup(),
                                 IdentityPreprocessor())
