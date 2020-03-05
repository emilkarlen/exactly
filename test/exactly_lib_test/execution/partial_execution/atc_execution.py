import os
import pathlib
import subprocess
import sys
import unittest
from typing import Dict

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.phase_step import SimplePhaseStep
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.section_document.model import new_empty_section_contents
from exactly_lib.test_case.actor import ActionToCheck, Actor, ParseException, AtcOsProcessExecutor
from exactly_lib.test_case.os_services import DEFAULT_ATC_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.partial_execution.test_resources.act_phase_handling import \
    actor_for_execution_of_python_source
from exactly_lib_test.execution.partial_execution.test_resources.arrange_and_expect import execute_and_check, \
    Arrangement, Expectation
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActionToCheckWrapperThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatJustReturnsSuccess, ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantAtc
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_checks import FileChecker
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir, tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import file_assertions as fa
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecutionSequence),
        unittest.makeSuite(TestCurrentDirectory),
        unittest.makeSuite(TestExecute),
    ])


class CwdRegisterer:
    def __init__(self):
        self._phase_step_2_cwd = {}

    @property
    def phase_step_2_cwd(self) -> Dict[SimplePhaseStep, pathlib.Path]:
        return self._phase_step_2_cwd

    def register_cwd_for(self, step):
        self._phase_step_2_cwd[step] = pathlib.Path.cwd()


class TestExecutionSequence(unittest.TestCase):
    def test_WHEN_parse_raises_parse_exception_THEN_execution_SHOULD_stop_with_result_of_validation_error(self):
        # ARRANGE #
        expected_cause = svh.new_svh_validation_error__str('failure message')
        atc_that_does_nothing = ActionToCheckThatRunsConstantActions()
        step_recorder = ListRecorder()
        recording_atc = ActionToCheckWrapperThatRecordsSteps(step_recorder,
                                                             atc_that_does_nothing)
        actor = ActorForConstantAtc(
            recording_atc,
            parse_atc=do_raise(ParseException(expected_cause))
        )
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(phase_result=asrt_result.status_is(ExecutionFailureStatus.VALIDATION_ERROR))
        # APPLY #
        execute_and_check(self, arrangement, expectation)
        self.assertEqual([],
                         step_recorder.recorded_elements,
                         'executed steps')

    def test_WHEN_parse_raises_unknown_exception_THEN_execution_SHOULD_stop_with_result_of_implementation_error(self):
        # ARRANGE #
        atc_that_does_nothing = ActionToCheckThatRunsConstantActions()
        step_recorder = ListRecorder()
        recording_atc = ActionToCheckWrapperThatRecordsSteps(step_recorder,
                                                             atc_that_does_nothing)
        actor = ActorForConstantAtc(
            recording_atc,
            parse_atc=do_raise(ValueError('failure message'))
        )
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(phase_result=asrt_result.status_is(ExecutionFailureStatus.IMPLEMENTATION_ERROR))
        # APPLY #
        execute_and_check(self, arrangement, expectation)
        self.assertEqual([],
                         step_recorder.recorded_elements,
                         'executed steps')


class TestCurrentDirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE
        cwd_registerer = CwdRegisterer()
        with tmp_dir_as_cwd() as expected_current_directory_pre_validate_post_setup:
            atc_that_records_current_dir = _ActionToCheckThatRecordsCurrentDir(cwd_registerer)
            actor = ActorForConstantAtc(atc_that_records_current_dir)
            # ACT #
            _execute(actor, _empty_test_case(),
                     current_directory=expected_current_directory_pre_validate_post_setup)
            # ASSERT #
            phase_step_2_cwd = cwd_registerer.phase_step_2_cwd
            sds = atc_that_records_current_dir.actual_sds
            self.assertEqual(len(phase_step_2_cwd),
                             4,
                             'Expects recordings for 4 steps')
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
        executor = _AtcThatReturnsConstantExitCode(exit_code_from_execution)
        actor = ActorForConstantAtc(executor)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(assertion_on_sds=_exit_code_result_file_contains(str(exit_code_from_execution)))
        # APPLY #
        execute_and_check(self, arrangement, expectation)

    def test_stdout_should_be_saved_in_file(self):
        # ARRANGE #
        python_source = _PYTHON_PROGRAM_THAT_WRITES_VALUE_TO_FILE.format(file='stdout',
                                                                         value='output from program')
        actor = actor_for_execution_of_python_source(python_source)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(assertion_on_sds=_stdout_result_file_contains('output from program'))
        # APPLY #
        execute_and_check(self, arrangement, expectation)

    def test_stderr_should_be_saved_in_file(self):
        # ARRANGE #
        python_source = _PYTHON_PROGRAM_THAT_WRITES_VALUE_TO_FILE.format(file='stderr',
                                                                         value='output from program')
        actor = actor_for_execution_of_python_source(python_source)
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(assertion_on_sds=_stderr_result_file_contains('output from program'))
        # APPLY #
        execute_and_check(self, arrangement, expectation)

    def test_WHEN_stdin_set_to_file_that_does_not_exist_THEN_execution_should_result_in_hard_error(self):
        # ARRANGE #
        setup_settings = setup.default_settings()
        setup_settings.stdin.file_name = 'this-is-not-the-name-of-an-existing-file.txt'
        actor = ActorForConstantAtc(ActionToCheckThatJustReturnsSuccess())
        test_case = _empty_test_case()
        # ACT #
        result = _execute(actor, test_case, setup_settings)
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


def _exit_code_result_file_contains(expected_contents: str) -> ValueAssertion:
    return asrt.sub_component('file for exit code',
                              lambda sds: sds.result.exitcode_file,
                              fa.path_is_file_with_contents(expected_contents))


def _stdout_result_file_contains(expected_contents: str) -> ValueAssertion:
    return asrt.sub_component('file for stdout',
                              lambda sds: sds.result.stdout_file,
                              fa.path_is_file_with_contents(expected_contents))


def _stderr_result_file_contains(expected_contents: str) -> ValueAssertion:
    return asrt.sub_component('file for stderr',
                              lambda sds: sds.result.stderr_file,
                              fa.path_is_file_with_contents(expected_contents))


def _check_contents_of_stdin_for_setup_settings(put: unittest.TestCase,
                                                setup_settings: SetupSettingsBuilder,
                                                expected_contents_of_stdin: str) -> PartialExeResult:
    """
    Tests contents of stdin by executing a Python program that stores
    the contents of stdin in a file.
    """
    with tmp_dir() as tmp_dir_path:
        with preserved_cwd():
            # ARRANGE #
            output_file_path = tmp_dir_path / 'output.txt'
            python_program_file = fs.File('logic_symbol_utils.py',
                                          _python_program_that_prints_stdin_to(output_file_path))
            python_program_file.write_to(tmp_dir_path)
            executor_that_records_contents_of_stdin = _AtcThatExecutesPythonProgramFile(
                tmp_dir_path / 'logic_symbol_utils.py')
            parser = ActorForConstantAtc(
                executor_that_records_contents_of_stdin)
            test_case = _empty_test_case()
            # ACT #
            result = _execute(parser, test_case, setup_settings)
            # ASSERT #
            file_checker = FileChecker(put)
            file_checker.assert_file_contents(output_file_path,
                                              expected_contents_of_stdin)
            return result


class _ActionToCheckThatRecordsCurrentDir(ActionToCheck):
    def __init__(self, cwd_registerer: CwdRegisterer):
        self._actual_sds = None
        self.cwd_registerer = cwd_registerer

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        self.cwd_registerer.register_cwd_for(phase_step.ACT__VALIDATE_PRE_SDS)
        return svh.new_svh_success()

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        self._actual_sds = environment.sds
        self.cwd_registerer.register_cwd_for(phase_step.ACT__VALIDATE_POST_SETUP)
        return svh.new_svh_success()

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.cwd_registerer.register_cwd_for(phase_step.ACT__PREPARE)
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.cwd_registerer.register_cwd_for(phase_step.ACT__EXECUTE)
        return new_eh_exit_code(0)

    @property
    def actual_sds(self) -> SandboxDirectoryStructure:
        return self._actual_sds


class _AtcThatExecutesPythonProgramFile(ActionToCheckThatJustReturnsSuccess):
    def __init__(self, python_program_file: pathlib.Path):
        self.python_program_file = python_program_file

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        exit_code = subprocess.call([sys.executable, str(self.python_program_file)],
                                    timeout=60,
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)


class _AtcThatReturnsConstantExitCode(ActionToCheckThatJustReturnsSuccess):
    def __init__(self, exit_code: int):
        self.exit_code = exit_code

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_process_executor: AtcOsProcessExecutor,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return new_eh_exit_code(self.exit_code)


def _empty_test_case() -> TestCase:
    return TestCase(new_empty_section_contents(),
                    new_empty_section_contents(),
                    new_empty_section_contents(),
                    new_empty_section_contents(),
                    new_empty_section_contents())


def _execute(actor: Actor,
             test_case: TestCase,
             setup_settings: SetupSettingsBuilder = setup.default_settings(),
             is_keep_sandbox: bool = False,
             current_directory: pathlib.Path = None,
             ) -> PartialExeResult:
    if current_directory is None:
        current_directory = pathlib.Path.cwd()
    with home_directory_structure() as hds:
        with preserved_cwd():
            os.chdir(str(current_directory))
            return sut.execute(
                test_case,
                ExecutionConfiguration(dict(os.environ),
                                       DEFAULT_ATC_OS_PROCESS_EXECUTOR,
                                       sandbox_root_name_resolver.for_test()),
                ConfPhaseValues(actor,
                                hds),
                setup_settings,
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
