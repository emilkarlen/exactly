import types
import unittest

from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.result import sh, svh
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording, TestCaseGeneratorWithRecordingInstrFollowedByExtraInstrsInEachPhase
from exactly_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from exactly_lib_test.execution.test_resources.execution_recording import actor
from exactly_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from exactly_lib_test.tcfs.test_resources.sds_check.sds_assertions import is_sds_root_dir
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.execute_methods import ExecuteFunctionEh
from exactly_lib_test.test_case.actor.test_resources.test_actions import validate_action_that_returns, \
    execute_action_that_returns_exit_code, prepare_action_that_returns
from exactly_lib_test.test_resources.actions import do_nothing
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement(tuple):
    def __new__(cls,
                test_case_generator: TestCaseGeneratorForExecutionRecording,
                parse_action=do_nothing,
                validate_test_action=validate_action_that_returns(svh.new_svh_success()),
                prepare_test_action=prepare_action_that_returns(sh.new_sh_success()),
                execute_test_action: ExecuteFunctionEh = execute_action_that_returns_exit_code(),
                act_executor_validate_pre_sds=validate_action_that_returns(svh.new_svh_success())):
        return tuple.__new__(cls, (test_case_generator,
                                   validate_test_action,
                                   act_executor_validate_pre_sds,
                                   prepare_test_action,
                                   execute_test_action,
                                   parse_action))

    @property
    def test_case_generator(self) -> TestCaseGeneratorForExecutionRecording:
        return self[0]

    @property
    def parse(self) -> types.FunctionType:
        return self[5]

    @property
    def validate_test_action(self) -> types.FunctionType:
        return self[1]

    @property
    def act_executor_validate_pre_sds(self) -> types.FunctionType:
        return self[2]

    @property
    def prepare_test_action(self) -> types.FunctionType:
        return self[3]

    @property
    def execute_test_action(self) -> ExecuteFunctionEh:
        return self[4]


class Expectation(tuple):
    def __new__(cls,
                expected_result: ValueAssertion[FullExeResult],
                expected_internal_recording: list):
        return tuple.__new__(cls, (expected_result,
                                   expected_internal_recording,
                                   ))

    @property
    def full_result(self) -> ValueAssertion[FullExeResult]:
        return self[0]

    @property
    def internal_recording(self) -> list:
        return self[1]


class _TestCaseThatRecordsExecution(FullExecutionTestCaseBase):
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expectation: Expectation,
                 dbg_do_not_delete_dir_structure=False,
                 actor: Actor = None,
                 recorder: ListRecorder = None):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure,
                         actor)
        self._test_case_generator = test_case_generator
        self.__expectation = expectation
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = test_case_generator.recorder

    def _test_case(self) -> test_case_doc.TestCase:
        return self._test_case_generator.test_case

    def _assertions(self):
        self.__expectation.full_result.apply_with_message(self.utc,
                                                          self.full_result,
                                                          'full_result')
        if self.full_result.has_sds:
            is_sds_root_dir().apply_with_message(self.utc, str(self.sds.root_dir),
                                                 'SDS root dir')

        msg = 'Difference in the sequence of executed phases and steps that are executed internally'
        self.utc.assertListEqual(self.__expectation.internal_recording,
                                 self.__recorder.recorded_elements,
                                 msg)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               arrangement: Arrangement,
               expectation: Expectation,
               dbg_do_not_delete_dir_structure=False):
        self._new_test_case_with_recording(arrangement,
                                           expectation,
                                           dbg_do_not_delete_dir_structure).execute()

    def _new_test_case_with_recording(self,
                                      arrangement: Arrangement,
                                      expectation: Expectation,
                                      dbg_do_not_delete_dir_structure=False) -> _TestCaseThatRecordsExecution:
        actor = self._with_recording_act_program_executor(arrangement)
        return _TestCaseThatRecordsExecution(self,
                                             arrangement.test_case_generator,
                                             expectation,
                                             dbg_do_not_delete_dir_structure,
                                             actor,
                                             arrangement.test_case_generator.recorder)

    def _with_recording_act_program_executor(self,
                                             arrangement: Arrangement) -> Actor:
        constant_actions_atc = ActionToCheckThatRunsConstantActions(
            validate_post_setup_action=arrangement.validate_test_action,
            prepare_action=arrangement.prepare_test_action,
            execute_action=arrangement.execute_test_action,
            validate_pre_sds_action=arrangement.act_executor_validate_pre_sds)
        return actor.actor_of_constant(
            arrangement.test_case_generator.recorder,
            constant_actions_atc,
            parse_action=arrangement.parse)


def one_successful_instruction_in_each_phase() -> TestCaseGeneratorForExecutionRecording:
    return TestCaseGeneratorWithRecordingInstrFollowedByExtraInstrsInEachPhase()
