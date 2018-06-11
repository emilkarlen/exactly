import types
import unittest
from typing import Optional

from exactly_lib.execution.partial_execution.result import PartialResultStatus
from exactly_lib.execution.result import ActionToCheckOutcome
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.result import sh, svh
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.test_case_base import PartialExecutionTestCaseBase
from exactly_lib_test.execution.test_resources.act_source_executor import ActSourceAndExecutorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorWrapperConstructorThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from exactly_lib_test.execution.test_resources.test_actions import execute_action_that_returns_exit_code, \
    prepare_action_that_returns
from exactly_lib_test.test_resources.actions import do_nothing, do_return
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Arrangement(tuple):
    def __new__(cls,
                test_case_generator: TestCaseGeneratorForExecutionRecording,
                act_executor_parse=do_nothing,
                act_executor_validate_post_setup=do_return(svh.new_svh_success()),
                act_executor_prepare=prepare_action_that_returns(sh.new_sh_success()),
                act_executor_execute=execute_action_that_returns_exit_code(),
                act_executor_validate_pre_sds=do_return(svh.new_svh_success()),
                act_executor_symbol_usages=do_return([])
                ):
        return tuple.__new__(cls, (test_case_generator,
                                   act_executor_validate_post_setup,
                                   act_executor_prepare,
                                   act_executor_execute,
                                   act_executor_validate_pre_sds,
                                   act_executor_symbol_usages,
                                   act_executor_parse))

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

    @property
    def act_executor_symbol_usages(self) -> types.FunctionType:
        return self[5]

    @property
    def act_executor_parse(self) -> types.FunctionType:
        return self[6]


class Expectation(tuple):
    def __new__(cls,
                expected_status: PartialResultStatus,
                expected_action_to_check_outcome: asrt.ValueAssertion[Optional[ActionToCheckOutcome]],
                expected_failure_info: ExpectedFailure,
                expected_internal_recording: list,
                sandbox_directory_structure_should_exist: bool):
        return tuple.__new__(cls, (expected_status,
                                   expected_failure_info,
                                   expected_internal_recording,
                                   sandbox_directory_structure_should_exist,
                                   expected_action_to_check_outcome))

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
    def sandbox_directory_structure_should_exist(self) -> bool:
        return self[3]

    @property
    def expected_action_to_check_outcome(self) -> asrt.ValueAssertion[Optional[ActionToCheckOutcome]]:
        return self[4]


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
        msg = 'Difference in the sequence of executed phases and steps'
        self.put.assertListEqual(self.__expectation.internal_recording,
                                 self.__recorder.recorded_elements,
                                 msg)

        if self.__expectation.sandbox_directory_structure_should_exist:
            self.put.assertTrue(self.partial_result.has_sds)
            self.put.assertIsNotNone(self.partial_result.sds)
        else:
            self.put.assertFalse(self.partial_result.has_sds)
            self.put.assertIsNone(self.partial_result.sds)

        self.__expectation.expected_action_to_check_outcome.apply_with_message(
            self.put,
            self.partial_result.action_to_check_outcome,
            'action-to-check-outcome')


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
        symbol_usages_action=arrangement.act_executor_symbol_usages,
        parse_action=arrangement.act_executor_parse,
        validate_pre_sds_action=arrangement.act_executor_validate_pre_sds,
        validate_post_setup_action=arrangement.act_executor_validate_post_setup,
        prepare_action=arrangement.act_executor_prepare,
        execute_action=arrangement.act_executor_execute,
    )
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
