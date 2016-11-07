import types
import unittest

from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.test_case_base import PartialExecutionTestCaseBase
from exactly_lib_test.execution.test_resources.act_source_executor import ActSourceAndExecutorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorWrapperConstructorThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from exactly_lib_test.execution.test_resources.test_actions import validate_action_that_returns, \
    execute_action_that_returns_exit_code, prepare_action_that_returns
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailure


class Arrangement(tuple):
    def __new__(cls,
                test_case_generator: TestCaseGeneratorForExecutionRecording,
                act_executor_validate_post_setup=validate_action_that_returns(svh.new_svh_success()),
                act_executor_prepare=prepare_action_that_returns(sh.new_sh_success()),
                act_executor_execute=execute_action_that_returns_exit_code(),
                act_executor_validate_pre_sds=validate_action_that_returns(svh.new_svh_success()),
                ):
        return tuple.__new__(cls, (test_case_generator,
                                   act_executor_validate_post_setup,
                                   act_executor_prepare,
                                   act_executor_execute,
                                   act_executor_validate_pre_sds))

    @property
    def test_case_generator(self) -> TestCaseGeneratorForExecutionRecording:
        return self[0]

    @property
    def act_executor_validate_post_setup(self) -> types.FunctionType:
        return self[1]

    @property
    def act_executor_validate_pre_sds(self) -> types.FunctionType:
        return self[4]

    @property
    def act_executor_prepare(self) -> types.FunctionType:
        return self[2]

    @property
    def act_executor_execute(self) -> types.FunctionType:
        return self[3]


class Expectation(tuple):
    def __new__(cls,
                expected_status: PartialResultStatus,
                expected_failure_info: ExpectedFailure,
                expected_internal_recording: list,
                execution_directory_structure_should_exist: bool):
        return tuple.__new__(cls, (expected_status,
                                   expected_failure_info,
                                   expected_internal_recording,
                                   execution_directory_structure_should_exist))

    @property
    def status(self) -> PartialResultStatus:
        return self[0]

    @property
    def failure_info(self) -> ExpectedFailure:
        return self[1]

    @property
    def internal_recording(self) -> list:
        return self[2]

    @property
    def execution_directory_structure_should_exist(self) -> bool:
        return self[3]


class _TestCaseThatRecordsExecution(PartialExecutionTestCaseBase):
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 put: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expectation: Expectation,
                 dbg_do_not_delete_dir_structure=False,
                 act_phase_handling: ActPhaseHandling = None,
                 recorder: ListRecorder = None):
        super().__init__(put,
                         dbg_do_not_delete_dir_structure,
                         act_phase_handling)
        self._test_case_generator = test_case_generator
        self.__expectation = expectation
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = test_case_generator.recorder

    def _test_case(self) -> test_case_doc.TestCase:
        return self._test_case_generator.test_case

    def _assertions(self):
        self.put.assertEqual(self.__expectation.status,
                             self.partial_result.status,
                             'Unexpected result status')
        self.__expectation.failure_info.assertions(self.put,
                                                   self.partial_result.failure_info)
        msg = 'Difference in the sequence of executed phases and steps that are executed internally'
        self.put.assertEqual(self.__expectation.internal_recording,
                             self.__recorder.recorded_elements,
                             msg)
        if self.__expectation.execution_directory_structure_should_exist:
            self.put.assertTrue(self.partial_result.has_execution_directory_structure)
            self.put.assertIsNotNone(self.partial_result.execution_directory_structure)
        else:
            self.put.assertFalse(self.partial_result.has_execution_directory_structure)
            self.put.assertIsNone(self.partial_result.execution_directory_structure)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation,
               dbg_do_not_delete_dir_structure=False):
        execute_test_case_with_recording(self,
                                         arrangement,
                                         expectation,
                                         dbg_do_not_delete_dir_structure)


def execute_test_case_with_recording(put: unittest.TestCase,
                                     arrangement: Arrangement,
                                     expectation: Expectation,
                                     dbg_do_not_delete_dir_structure=False):
    constant_actions_runner = ActSourceAndExecutorThatRunsConstantActions(
        validate_post_setup_action=arrangement.act_executor_validate_post_setup,
        prepare_action=arrangement.act_executor_prepare,
        execute_action=arrangement.act_executor_execute,
        validate_pre_sds_action=arrangement.act_executor_validate_pre_sds)
    constructor = ActSourceAndExecutorWrapperConstructorThatRecordsSteps(
        arrangement.test_case_generator.recorder,
        constant_actions_runner)
    act_phase_handling = ActPhaseHandling(constructor)
    test_case = _TestCaseThatRecordsExecution(put,
                                              arrangement.test_case_generator,
                                              expectation,
                                              dbg_do_not_delete_dir_structure,
                                              act_phase_handling,
                                              arrangement.test_case_generator.recorder)
    test_case.execute()
