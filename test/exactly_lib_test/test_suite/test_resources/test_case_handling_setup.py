from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions


def test_case_handling_setup_with_identity_preprocessor() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(ActSourceAndExecutorConstructorThatRunsConstantActions()),
                                 IDENTITY_PREPROCESSOR)
