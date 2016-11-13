import pathlib

from exactly_lib.execution import result
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import TestCaseSetup
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_suite import structure
from exactly_lib.util.failure_details import new_failure_details_from_message
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions


def test_case_handling_setup_with_identity_preprocessor() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup(ActSourceAndExecutorConstructorThatRunsConstantActions()),
                                 IDENTITY_PREPROCESSOR)


class TestCaseProcessorThatGivesConstant(test_case_processing.Processor):
    def __init__(self,
                 result: test_case_processing.Result):
        self.result = result

    def apply(self, test_case: test_case_processing.TestCaseSetup) -> test_case_processing.Result:
        return self.result


DUMMY_CASE_PROCESSING = case_processing.Configuration(
    lambda x: ((), ()),
    InstructionsSetup({}, {}, {}, {}, {}),
    test_case_handling_setup_with_identity_preprocessor(),
    False)

DUMMY_SDS = SandboxDirectoryStructure('test-root-dir')


def full_result_with_failure_info(status: result.FullResultStatus,
                                  failure_phase_step=phase_step.ASSERT__MAIN) -> result.FullResult:
    return result.FullResult(status,
                             DUMMY_SDS,
                             result.FailureInfo(failure_phase_step,
                                                new_failure_details_from_message('failure message')))


def full_result_without_failure_info(status: result.FullResultStatus) -> result.FullResult:
    return result.FullResult(status,
                             DUMMY_SDS,
                             None)


FULL_RESULT_PASS = result.new_pass(DUMMY_SDS)
FULL_RESULT_SKIP = result.new_skipped()
FULL_RESULT_FAIL = full_result_with_failure_info(result.FullResultStatus.FAIL)

T_C_H_S = test_case_handling_setup_with_identity_preprocessor()


def test_suite(source_file_name: str,
               sub_test_suites: list,
               test_cases: list) -> structure.TestSuite:
    return structure.TestSuite(pathlib.Path(source_file_name),
                               [],
                               T_C_H_S,
                               sub_test_suites,
                               test_cases)


def test_case(source_file_name: str) -> TestCaseSetup:
    return TestCaseSetup(pathlib.Path(source_file_name))
