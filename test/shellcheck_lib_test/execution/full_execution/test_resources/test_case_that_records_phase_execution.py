import pathlib
import unittest

from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib.default.execution_mode.test_case.processing import script_handling_for_setup
from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.partial_execution import ScriptHandling
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.general.std import StdFiles
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.full_execution.test_resources import \
    recording_instructions_for_sequence_tests as instr
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_base import FullExecutionTestCaseBase
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailure


class Expectation(tuple):
    def __new__(cls,
                expected_status: FullResultStatus,
                expected_failure_info: ExpectedFailure,
                expected_internal_recording: list,
                execution_directory_structure_should_exist: bool):
        return tuple.__new__(cls, (expected_status,
                                   expected_failure_info,
                                   expected_internal_recording,
                                   execution_directory_structure_should_exist))

    @property
    def status(self) -> FullResultStatus:
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


class TestCaseThatRecordsExecution(FullExecutionTestCaseBase):
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expectation: Expectation,
                 dbg_do_not_delete_dir_structure=False,
                 script_handling: ScriptHandling = None,
                 recorder: instr.ListRecorder = None):
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
                             self.full_result.status,
                             'Unexpected result status')
        self.__expectation.failure_info.assertions(self.utc,
                                                   self.full_result.failure_info)
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
                                  'Execution Directory Structure is expected to not be created')


def with_recording_act_program_executor(recorder: instr.ListRecorder,
                                        script_handling: ScriptHandling,
                                        validate_test_action,
                                        execute_test_action):
    return ScriptHandling(script_handling.builder,
                          _ActProgramExecutorWrapperThatRecordsSteps(recorder,
                                                                     script_handling.executor,
                                                                     validate_test_action,
                                                                     execute_test_action))


def validate_action_that_returns(ret_val: svh.SuccessOrValidationErrorOrHardError):
    def f():
        return ret_val

    return f


def validate_action_that_raises(ex: Exception):
    def f():
        raise ex

    return f


def execute_action_that_does_nothing():
    def f():
        pass

    return f


def execute_action_that_raises(ex: Exception):
    def f():
        raise ex

    return f


class _ActProgramExecutorWrapperThatRecordsSteps(ActProgramExecutor):
    def __init__(self,
                 recorder: instr.ListRecorder,
                 wrapped: ActProgramExecutor,
                 validate_test_action,
                 execute_test_action):
        self.__recorder = recorder
        self.__wrapped = wrapped
        self.__validate_test_action = validate_test_action
        self.__execute_test_action = execute_test_action

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__SCRIPT_VALIDATE).record()
        test_action_result = self.__validate_test_action()
        if not test_action_result.is_success:
            return test_action_result
        return self.__wrapped.validate(home_dir, source)

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        self.__wrapped.prepare(source_setup, home_dir_path, eds)

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> int:
        self.__recorder.recording_of(phase_step.ACT__SCRIPT_EXECUTE).record()
        self.__execute_test_action()
        return self.__wrapped.execute(source_setup,
                                      home_dir,
                                      eds,
                                      std_files)


def new_test_case_with_recording(unittest_case: unittest.TestCase,
                                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                                 expectation: Expectation,
                                 validate_test_action=validate_action_that_returns(svh.new_svh_success()),
                                 execute_test_action=execute_action_that_does_nothing(),
                                 dbg_do_not_delete_dir_structure=False) -> TestCaseThatRecordsExecution:
    script_handling = with_recording_act_program_executor(test_case_generator.recorder,
                                                          script_handling_for_setup(python3.new_act_phase_setup()),
                                                          validate_test_action,
                                                          execute_test_action)
    return TestCaseThatRecordsExecution(unittest_case,
                                        test_case_generator,
                                        expectation,
                                        dbg_do_not_delete_dir_structure,
                                        script_handling,
                                        test_case_generator.recorder)
