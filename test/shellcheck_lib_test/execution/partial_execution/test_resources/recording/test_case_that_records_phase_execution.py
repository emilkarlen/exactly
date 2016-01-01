import types
import unittest

from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib.default.execution_mode.test_case.processing import script_handling_for_setup
from shellcheck_lib.execution.partial_execution import ScriptHandling
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording, TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_base import PartialExecutionTestCaseBase
from shellcheck_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActProgramExecutorWrapperThatRecordsSteps
from shellcheck_lib_test.execution.test_resources.execution_recording.recorder import \
    ListRecorder
from shellcheck_lib_test.execution.test_resources.test_actions import validate_action_that_returns, \
    execute_action_that_does_nothing
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailure


class Arrangement(tuple):
    def __new__(cls,
                test_case_generator: TestCaseGeneratorForExecutionRecording,
                validate_test_action=validate_action_that_returns(svh.new_svh_success()),
                execute_test_action=execute_action_that_does_nothing()):
        return tuple.__new__(cls, (test_case_generator,
                                   validate_test_action,
                                   execute_test_action))

    @property
    def test_case_generator(self) -> TestCaseGeneratorForExecutionRecording:
        return self[0]

    @property
    def validate_test_action(self) -> types.FunctionType:
        return self[1]

    @property
    def execute_test_action(self) -> types.FunctionType:
        return self[2]


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
                 unittest_case: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expectation: Expectation,
                 dbg_do_not_delete_dir_structure=False,
                 script_handling: ScriptHandling = None,
                 recorder: ListRecorder = None):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure,
                         script_handling)
        self._test_case_generator = test_case_generator
        self.__expectation = expectation
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = test_case_generator.recorder

    def _test_case(self) -> test_case_doc.TestCase:
        return self._test_case_generator.test_case

    def _assertions(self):
        self.utc.assertEqual(self.__expectation.status,
                             self.partial_result.status,
                             'Unexpected result status')
        self.__expectation.failure_info.assertions(self.utc,
                                                   self.partial_result.failure_info)
        msg = 'Difference in the sequence of executed phases and steps that are executed internally'
        self.utc.assertEqual(self.__expectation.internal_recording,
                             self.__recorder.recorded_elements,
                             msg)
        if self.__expectation.execution_directory_structure_should_exist:
            self.utc.assertIsNotNone(self.eds)
            self.utc.assertTrue(
                    self.eds.root_dir.is_dir(),
                    'Execution Directory Structure root is expected to be a directory')
        else:
            self.utc.assertIsNone(self.eds,
                                  'Execution Directory Structure is expected to not have been created')


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
        script_handling = self._with_recording_act_program_executor(
                arrangement.test_case_generator.recorder,
                script_handling_for_setup(python3.new_act_phase_setup()),
                arrangement.validate_test_action,
                arrangement.execute_test_action)
        return _TestCaseThatRecordsExecution(self,
                                             arrangement.test_case_generator,
                                             expectation,
                                             dbg_do_not_delete_dir_structure,
                                             script_handling,
                                             arrangement.test_case_generator.recorder)

    def _with_recording_act_program_executor(self,
                                             recorder: ListRecorder,
                                             script_handling: ScriptHandling,
                                             validate_test_action,
                                             execute_test_action) -> ScriptHandling:
        return ScriptHandling(script_handling.builder,
                              ActProgramExecutorWrapperThatRecordsSteps(recorder,
                                                                        script_handling.executor,
                                                                        validate_test_action,
                                                                        execute_test_action))


def one_successful_instruction_in_each_phase() -> TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList:
    return TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()
