import pathlib
from typing import List, Dict

from exactly_lib.execution.full_execution.result import FullExeResultStatus, new_pass, new_skipped
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing import test_case_processing as tcp
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import TestCaseFileReference
from exactly_lib.test_suite import structure
from exactly_lib_test.execution.full_execution.test_resources.result_values import DUMMY_SDS, \
    full_result_with_failure_info
from exactly_lib_test.processing.test_resources.test_case_setup import \
    test_case_definition_with_no_instructions_and_no_preprocessor
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatJustReturnsConstant


def test_case_handling_setup_with_identity_preprocessor() -> TestCaseHandlingSetup:
    return TestCaseHandlingSetup(ActPhaseSetup('actor that does nothing',
                                               ActorThatRunsConstantActions()),
                                 IDENTITY_PREPROCESSOR)


class TestCaseProcessorThatGivesConstant(tcp.Processor):
    def __init__(self,
                 result: tcp.Result):
        self.result = result

    def apply(self, test_case: tcp.TestCaseFileReference) -> tcp.Result:
        return self.result


class TestCaseProcessorThatGivesConstantPerCase(tcp.Processor):
    """
    Processor that associates object ID:s of TestCaseSetup:s (Pythons internal id of objects, given
    by the id() method), with a processing result.

    Only TestCaseSetup:s that are included in this association (dict) can be executed.
    """

    def __init__(self,
                 test_case_id_2_result: Dict[int, tcp.Result]):
        self.test_case_id_2_result = test_case_id_2_result

    def apply(self, test_case: TestCaseFileReference) -> tcp.Result:
        return self.test_case_id_2_result[id(test_case)]


DUMMY_TEST_CASE_DEFINITION = test_case_definition_with_no_instructions_and_no_preprocessor()

DUMMY_CASE_PROCESSING = case_processing.Configuration(
    DUMMY_TEST_CASE_DEFINITION,
    test_case_handling_setup_with_identity_preprocessor(),
    os_services_access.new_for_cmd_exe(CommandExecutorThatJustReturnsConstant()),
    2 ** 10,
    False,
)

FULL_RESULT_PASS = new_pass(DUMMY_SDS, ActionToCheckOutcome(0))
FULL_RESULT_SKIP = new_skipped()
FULL_RESULT_FAIL = full_result_with_failure_info(FullExeResultStatus.FAIL)

T_C_H_S = test_case_handling_setup_with_identity_preprocessor()


def test_suite(source_file_name: str,
               sub_test_suites: List[structure.TestSuiteHierarchy],
               test_cases: List[TestCaseFileReference]) -> structure.TestSuiteHierarchy:
    return structure.TestSuiteHierarchy(pathlib.Path(source_file_name),
                                        [],
                                        T_C_H_S,
                                        sub_test_suites,
                                        test_cases)


def test_case(source_file_name: str) -> TestCaseFileReference:
    return TestCaseFileReference(pathlib.Path(source_file_name),
                                 pathlib.Path.cwd())
