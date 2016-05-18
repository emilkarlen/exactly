from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.cli.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.preprocessor import IdentityPreprocessor


def test_case_handling_setup() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(single_command_setup.act_phase_setup(),
                                 IdentityPreprocessor())
