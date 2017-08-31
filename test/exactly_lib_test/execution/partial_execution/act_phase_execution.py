import os
import pathlib
import subprocess
import sys
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution as sut
from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.section_document.model import new_empty_section_contents
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor, \
    ActPhaseHandling, ActSourceAndExecutorConstructor, ParseException
from exactly_lib.test_case.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.partial_execution.test_resources.arrange_and_expect import execute_and_check, \
    Arrangement, Expectation
from exactly_lib_test.execution.test_resources.act_source_executor import ActSourceAndExecutorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorConstructorForConstantExecutor, ActSourceAndExecutorThatJustReturnsSuccess, \
    ActSourceAndExecutorWrapperThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder
from exactly_lib_test.execution.test_resources.partial_result_check import partial_result_status_is
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.assertions.file_checks import FileChecker
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir, tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import file_assertions as fa
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionSequence),
        unittest.makeSuite(TestCurrentDirectory),
        unittest.makeSuite(TestExecute),
    ])


class TestExecutionSequence(unittest.TestCase):
    def test_WHEN_parse_raises_parse_exception_THEN_execution_SHOULD_stop_with_result_of_validation_error(self):
        # ARRANGE #
        expected_cause = svh.new_svh_validation_error('failure message')
        executor_with_parse_raises_parse_ex = ActSourceAndExecutorThatRunsConstantActions(
            parse_action=do_raise(ParseException(expected_cause))
        )
        step_recorder = ListRecorder()
        recording_executor = ActSourceAndExecutorWrapperThatRecordsSteps(step_recorder,
                                                                         executor_with_parse_raises_parse_ex)
        constructor = ActSourceAndExecutorConstructorForConstantExecutor(recording_executor)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  act_phase_handling=ActPhaseHandling(constructor))
        # ASSERT #
        expectation = Expectation(partial_result=partial_result_status_is(PartialResultStatus.VALIDATE))
        # APPLY #
        execute_and_check(self, arrangement, expectation)
        self.assertEqual([phase_step.ACT__PARSE],
                         step_recorder.recorded_elements,
                         'executed steps')

    def test_WHEN_parse_raises_unknown_exception_THEN_execution_SHOULD_stop_with_result_of_implementation_error(self):
        # ARRANGE #
        expected_cause = svh.new_svh_validation_error('failure message')
        executor_with_parse_raises_parse_ex = ActSourceAndExecutorThatRunsConstantActions(
            parse_action=do_raise(ValueError(expected_cause))
        )
        step_recorder = ListRecorder()
        recording_executor = ActSourceAndExecutorWrapperThatRecordsSteps(step_recorder,
                                                                         executor_with_parse_raises_parse_ex)
        constructor = ActSourceAndExecutorConstructorForConstantExecutor(recording_executor)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  act_phase_handling=ActPhaseHandling(constructor))
        # ASSERT #
        expectation = Expectation(partial_result=partial_result_status_is(PartialResultStatus.IMPLEMENTATION_ERROR))
        # APPLY #
        execute_and_check(self, arrangement, expectation)
        self.assertEqual([phase_step.ACT__PARSE],
                         step_recorder.recorded_elements,
                         'executed steps')


class TestCurrentDirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE
        with tmp_dir_as_cwd() as expected_current_directory_pre_validate_post_setup:
            executor_that_records_current_dir = _ExecutorThatRecordsCurrentDir()
            constructor = ActSourceAndExecutorConstructorForConstantExecutor(executor_that_records_current_dir)
            # ACT #
            _execute(constructor, _empty_test_case(),
                     current_directory=expected_current_directory_pre_validate_post_setup)
            # ASSERT #
            phase_step_2_cwd = executor_that_records_current_dir.phase_step_2_cwd
            sds = executor_that_records_current_dir.actual_sds
            self.assertEqual(len(phase_step_2_cwd),
                             5,
                             'Expects recordings for 5 steps')
            self.assertEqual(phase_step_2_cwd[phase_step.ACT__PARSE],
                             expected_current_directory_pre_validate_post_setup,
                             'Current dir for ' + str(phase_step.ACT__PARSE))
            self.assertEqual(phase_step_2_cwd[phase_step.ACT__VALIDATE_PRE_SDS],
                             expected_current_directory_pre_validate_post_setup,
                             'Current dir for ' + str(phase_step.ACT__VALIDATE_PRE_SDS))
            self.assertEqual(phase_step_2_cwd[phase_step.ACT__VALIDATE_POST_SETUP],
                             sds.act_dir,
                             'Current dir for ' + str(phase_step.ACT__VALIDATE_POST_SETUP))
            self.assertEqual(phase_step_2_cwd[phase_step.ACT__PREPARE],
                             sds.act_dir,
                             'Current dir for ' + str(phase_step.ACT__PREPARE))
            self.assertEqual(phase_step_2_cwd[phase_step.ACT__EXECUTE],
                             sds.act_dir,
                             'Current dir for ' + str(phase_step.ACT__EXECUTE))


class TestExecute(unittest.TestCase):
    def test_exitcode_should_be_saved_in_file(self):
        # ARRANGE #
        exit_code_from_execution = 72
        executor = _ExecutorThatReturnsConstantExitCode(exit_code_from_execution)
        constructor = ActSourceAndExecutorConstructorForConstantExecutor(executor)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  act_phase_handling=ActPhaseHandling(constructor))
        # ASSERT #
        expectation = Expectation(assertion_on_sds=_exit_code_result_file_contains(str(exit_code_from_execution)))
        # APPLY #
        execute_and_check(self, arrangement, expectation)

    def test_stdout_should_be_saved_in_file(self):
        # ARRANGE #
        python_source = _PYTHON_PROGRAM_THAT_WRITES_VALUE_TO_FILE.format(file='stdout',
                                                                         value='output from program')
        act_phase_handling = _act_phase_handling_for_execution_of_python_source(python_source)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  act_phase_handling=act_phase_handling)
        # ASSERT #
        expectation = Expectation(assertion_on_sds=_stdout_result_file_contains('output from program'))
        # APPLY #
        execute_and_check(self, arrangement, expectation)

    def test_stderr_should_be_saved_in_file(self):
        # ARRANGE #
        python_source = _PYTHON_PROGRAM_THAT_WRITES_VALUE_TO_FILE.format(file='stderr',
                                                                         value='output from program')
        act_phase_handling = _act_phase_handling_for_execution_of_python_source(python_source)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  act_phase_handling=act_phase_handling)
        # ASSERT #
        expectation = Expectation(assertion_on_sds=_stderr_result_file_contains('output from program'))
        # APPLY #
        execute_and_check(self, arrangement, expectation)

    def test_WHEN_stdin_set_to_file_that_does_not_exist_THEN_execution_should_result_in_hard_error(self):
        # ARRANGE #
        setup_settings = setup.default_settings()
        setup_settings.stdin.file_name = 'this-is-not-the-name-of-an-existing-file.txt'
        constructor = ActSourceAndExecutorConstructorForConstantExecutor(ActSourceAndExecutorThatJustReturnsSuccess())
        test_case = _empty_test_case()
        # ACT #
        result = _execute(constructor, test_case, setup_settings)
        # ASSERT #
        self.assertTrue(result.is_failure)

    def test_WHEN_stdin_set_to_file_THEN_it_SHOULD_consist_of_contents_of_this_file(self):
        file_to_redirect = fs.File('redirected-to-stdin.txt', 'contents of file to redirect')
        with tmp_dir(fs.DirContents([file_to_redirect])) as abs_tmp_dir_path:
            absolute_name_of_file_to_redirect = abs_tmp_dir_path / 'redirected-to-stdin.txt'
            setup_settings = setup.default_settings()
            setup_settings.stdin.file_name = absolute_name_of_file_to_redirect
            _check_contents_of_stdin_for_setup_settings(self,
                                                        setup_settings,
                                                        'contents of file to redirect')

    def test_WHEN_stdin_set_to_string_THEN_it_SHOULD_consist_of_this_string(self):
        setup_settings = setup.default_settings()
        setup_settings.stdin.contents = 'contents of stdin'
        _check_contents_of_stdin_for_setup_settings(self,
                                                    setup_settings,
                                                    'contents of stdin')

    def test_WHEN_stdin_is_not_set_in_setup_THEN_it_should_be_empty(self):
        setup_settings = setup.default_settings()
        setup_settings.stdin.set_empty()
        expected_contents_of_stdin = ''
        _check_contents_of_stdin_for_setup_settings(self,
                                                    setup_settings,
                                                    expected_contents_of_stdin)


def _exit_code_result_file_contains(expected_contents: str) -> asrt.ValueAssertion:
    return asrt.sub_component('file for exit code',
                              lambda sds: sds.result.exitcode_file,
                              fa.path_is_file_with_contents(expected_contents))


def _stdout_result_file_contains(expected_contents: str) -> asrt.ValueAssertion:
    return asrt.sub_component('file for stdout',
                              lambda sds: sds.result.stdout_file,
                              fa.path_is_file_with_contents(expected_contents))


def _stderr_result_file_contains(expected_contents: str) -> asrt.ValueAssertion:
    return asrt.sub_component('file for stderr',
                              lambda sds: sds.result.stderr_file,
                              fa.path_is_file_with_contents(expected_contents))


def _check_contents_of_stdin_for_setup_settings(put: unittest.TestCase,
                                                setup_settings: SetupSettingsBuilder,
                                                expected_contents_of_stdin: str) -> sut.PartialResult:
    """
    Tests contents of stdin by executing a Python program that stores
    the contents of stdin in a file.
    """
    with tmp_dir() as tmp_dir_path:
        with preserved_cwd():
            # ARRANGE #
            output_file_path = tmp_dir_path / 'output.txt'
            python_program_file = fs.File('program.py', _python_program_that_prints_stdin_to(output_file_path))
            python_program_file.write_to(tmp_dir_path)
            executor_that_records_contents_of_stdin = _ExecutorThatExecutesPythonProgramFile(
                tmp_dir_path / 'program.py')
            constructor = ActSourceAndExecutorConstructorForConstantExecutor(
                executor_that_records_contents_of_stdin)
            test_case = _empty_test_case()
            # ACT #
            result = _execute(constructor, test_case, setup_settings)
            # ASSERT #
            file_checker = FileChecker(put)
            file_checker.assert_file_contents(output_file_path,
                                              expected_contents_of_stdin)
            return result


class _ExecutorThatRecordsCurrentDir(ActSourceAndExecutor):
    def __init__(self):
        self._actual_sds = None
        self.phase_step_2_cwd = {}

    def parse(self, environment: InstructionEnvironmentForPreSdsStep):
        self._register_cwd_for(phase_step.ACT__PARSE)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        self._register_cwd_for(phase_step.ACT__VALIDATE_PRE_SDS)
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        self._actual_sds = environment.sds
        self._register_cwd_for(phase_step.ACT__VALIDATE_POST_SETUP)
        return svh.new_svh_success()

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self._register_cwd_for(phase_step.ACT__PREPARE)
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self._register_cwd_for(phase_step.ACT__EXECUTE)
        return new_eh_exit_code(0)

    def _register_cwd_for(self, step):
        self.phase_step_2_cwd[step] = pathlib.Path.cwd()

    @property
    def actual_sds(self) -> SandboxDirectoryStructure:
        return self._actual_sds


class _ExecutorThatExecutesPythonProgramFile(ActSourceAndExecutorThatJustReturnsSuccess):
    def __init__(self, python_program_file: pathlib.Path):
        self.python_program_file = python_program_file

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        exit_code = subprocess.call([sys.executable, str(self.python_program_file)],
                                    timeout=60,
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)


class _ExecutorThatExecutesPythonProgramSource(ActSourceAndExecutorThatJustReturnsSuccess):
    PYTHON_FILE_NAME = 'program.py'

    def __init__(self, python_program_source: str):
        self.python_program_source = python_program_source

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        python_file = pathlib.Path() / self.PYTHON_FILE_NAME
        with python_file.open(mode='w') as f:
            f.write(self.python_program_source)

        exit_code = subprocess.call([sys.executable, str(python_file)],
                                    timeout=60,
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)


def _act_phase_handling_for_execution_of_python_source(python_source: str) -> ActPhaseHandling:
    executor = _ExecutorThatExecutesPythonProgramSource(python_source)
    constructor = ActSourceAndExecutorConstructorForConstantExecutor(executor)
    return ActPhaseHandling(constructor)


class _ExecutorThatReturnsConstantExitCode(ActSourceAndExecutorThatJustReturnsSuccess):
    def __init__(self, exit_code: int):
        self.exit_code = exit_code

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return new_eh_exit_code(self.exit_code)


def _empty_test_case() -> sut.TestCase:
    return sut.TestCase(new_empty_section_contents(),
                        new_empty_section_contents(),
                        new_empty_section_contents(),
                        new_empty_section_contents(),
                        new_empty_section_contents())


def _execute(constructor: ActSourceAndExecutorConstructor,
             test_case: sut.TestCase,
             setup_settings: SetupSettingsBuilder = setup.default_settings(),
             is_keep_sandbox: bool = False,
             current_directory: pathlib.Path = None,
             ) -> sut.PartialResult:
    if current_directory is None:
        current_directory = pathlib.Path.cwd()
    with home_directory_structure() as hds:
        with preserved_cwd():
            os.chdir(str(current_directory))
            return sut.execute(
                ActPhaseHandling(constructor),
                test_case,
                sut.Configuration(ACT_PHASE_OS_PROCESS_EXECUTOR,
                                  hds,
                                  dict(os.environ)),
                setup_settings,
                program_info.PROGRAM_NAME + '-test-',
                is_keep_sandbox)


def _python_program_that_prints_stdin_to(output_file_path: pathlib.Path) -> str:
    return _PYTHON_PROGRAM_THAT_PRINTS_STDIN_TO_FILE_NAME.format(file_name=str(output_file_path))


_PYTHON_PROGRAM_THAT_PRINTS_STDIN_TO_FILE_NAME = """\
import sys

output_file = '{file_name}'

with open(output_file, mode='w') as f:
    f.write(sys.stdin.read())
"""

_PYTHON_PROGRAM_THAT_WRITES_VALUE_TO_FILE = """\
import sys

sys.{file}.write('{value}')
"""

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
