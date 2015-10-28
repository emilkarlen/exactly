import pathlib
import unittest

from shellcheck_lib.default.execution_mode.test_case.processing import script_handling_for_setup
from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.partial_execution import ScriptHandling

from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib_test.execution.full_execution.util import recording_instructions_for_sequence_tests as instr
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.full_execution.util.test_case_base import FullExecutionTestCaseBase
from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib_test.util.expected_instruction_failure import ExpectedFailure
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.execution.full_execution.util.recording_instructions_for_sequence_tests import \
    record_file_path
from shellcheck_lib_test.execution.full_execution.util.recording_instructions_for_sequence_tests import \
    record_file_contents_from_lines
from shellcheck_lib_test.execution.full_execution.util.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording


class TestCaseThatRecordsExecution(FullExecutionTestCaseBase):
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expected_status: FullResultStatus,
                 expected_failure_info: ExpectedFailure,
                 expected_internal_recording: list,
                 expected_file_recording: list,
                 execution_directory_structure_should_exist: bool,
                 dbg_do_not_delete_dir_structure=False,
                 script_handling: ScriptHandling=None,
                 recorder: instr.ListRecorder=None):
        super().__init__(unittest_case,
                         dbg_do_not_delete_dir_structure,
                         script_handling)
        self._test_case_generator = test_case_generator
        self.__expected_status = expected_status
        self.__expected_failure_info = expected_failure_info
        self.__expected_internal_instruction_recording = expected_internal_recording
        self.__expected_file_recording = expected_file_recording
        self.__execution_directory_structure_should_exist = execution_directory_structure_should_exist
        self.__recorder = recorder
        if self.__recorder is None:
            self.__recorder = test_case_generator.recorder

    def _test_case(self) -> test_case_doc.TestCase:
        return self._test_case_generator.test_case

    def _assertions(self):
        self.utc.assertEqual(self.__expected_status,
                             self.full_result.status,
                             'Unexpected result status')
        self.__expected_failure_info.assertions(self.utc,
                                                self.full_result.failure_info)
        msg = 'Difference in the sequence of executed phases and steps that are executed internally'
        self.utc.assertEqual(self.__expected_internal_instruction_recording,
                             self.__recorder.recorded_elements,
                             msg)
        if self.__execution_directory_structure_should_exist:
            self.utc.assertIsNotNone(self.eds)
            self.utc.assertTrue(
                self.eds.root_dir.is_dir(),
                'Execution Directory Structure root is expected to be a directory')
            file_path = record_file_path(self.eds)
            if not self.__expected_file_recording:
                self.utc.assertFalse(file_path.exists())
            else:
                expected_file_contents = record_file_contents_from_lines(self.__expected_file_recording)
                msg = 'Difference in sequence of phases/steps that are executed after Execution Directory Structure' + \
                      ' is created (recorded in file)'
                self.assert_is_regular_file_with_contents(file_path,
                                                          expected_file_contents,
                                                          msg)
        else:
            self.utc.assertIsNone(self.eds,
                                  'Execution Directory Structure is expected to not be created')


def with_recording_act_program_executor(recorder: instr.ListRecorder,
                                        script_handling: ScriptHandling):
    return ScriptHandling(script_handling.builder,
                          _ActProgramExecutorWrapperThatRecordsSteps(recorder,
                                                                     script_handling.executor))


class _ActProgramExecutorWrapperThatRecordsSteps(ActProgramExecutor):
    def __init__(self,
                 recorder: instr.ListRecorder,
                 wrapped: ActProgramExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def validate(self,
                 source: ScriptSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__SCRIPT_VALIDATION).record()
        return self.__wrapped.validate(source)

    def prepare(self,
                source_setup: SourceSetup,
                eds: ExecutionDirectoryStructure):
        return self.__wrapped.prepare(source_setup, eds)

    def execute(self,
                source_setup: SourceSetup,
                cwd_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                stdin,
                std_output_files: StdOutputFiles) -> int:
        self.__recorder.recording_of(phase_step.ACT__SCRIPT_EXECUTION).record()
        return self.__wrapped.execute(source_setup,
                                      cwd_dir_path,
                                      eds,
                                      stdin,
                                      std_output_files)


def new_test_case_with_recording(unittest_case: unittest.TestCase,
                                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                                 expected_status: FullResultStatus,
                                 expected_failure_info: ExpectedFailure,
                                 expected_internal_recording: list,
                                 expected_file_recording: list,
                                 execution_directory_structure_should_exist: bool,
                                 dbg_do_not_delete_dir_structure=False) -> TestCaseThatRecordsExecution:
    script_handling = with_recording_act_program_executor(test_case_generator.recorder,
                                                          script_handling_for_setup(python3.new_act_phase_setup()))
    return TestCaseThatRecordsExecution(unittest_case,
                                        test_case_generator,
                                        expected_status,
                                        expected_failure_info,
                                        expected_internal_recording,
                                        expected_file_recording,
                                        execution_directory_structure_should_exist,
                                        dbg_do_not_delete_dir_structure,
                                        script_handling,
                                        test_case_generator.recorder)
