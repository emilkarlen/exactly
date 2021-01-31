import os
import pathlib
import subprocess
import sys
import unittest
from typing import Dict, Optional

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.partial_execution.setup_settings_handler import StandardSetupSettingsHandler
from exactly_lib.execution.phase_step import SimplePhaseStep
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.types.string_source import as_stdin
from exactly_lib.impls.types.string_source import file_source
from exactly_lib.section_document.model import new_empty_section_contents
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import ActionToCheck, Actor, ParseException
from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code
from exactly_lib.type_val_deps.dep_variants.adv_w_validation.impls import ConstantAdvWValidation
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result, \
    settings_handlers
from exactly_lib_test.execution.partial_execution.test_resources.act_phase_utils import \
    actor_for_execution_of_python_source
from exactly_lib_test.execution.partial_execution.test_resources.arrange_and_expect import execute_and_check, \
    Arrangement, Expectation
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.execution.test_resources.execution_recording.action_to_check import \
    ActionToCheckWrapperThatRecordsSteps
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder
from exactly_lib_test.tcfs.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatJustReturnsSuccess, ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorForConstantAtc
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_checks import FileChecker
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir, tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import file_assertions as fa
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


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
    def test_WHEN_parse_raises_parse_exception_THEN_execution_SHOULD_stop_with_result_of_syntax_error(self):
        # ARRANGE #
        expected_cause = 'failure message'
        step_recorder = ListRecorder()
        recording_atc = ActionToCheckWrapperThatRecordsSteps(step_recorder,
                                                             _atc_that_does_nothing())
        actor = ActorForConstantAtc(
            recording_atc,
            parse_atc=do_raise(ParseException.of_str(expected_cause))
        )
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(phase_result=asrt_result.status_is(ExecutionFailureStatus.SYNTAX_ERROR))
        # APPLY #
        execute_and_check(self, arrangement, expectation)
        self.assertEqual([],
                         step_recorder.recorded_elements,
                         'executed steps')

    def test_WHEN_parse_raises_unknown_exception_THEN_execution_SHOULD_stop_with_result_of_internal_error(self):
        # ARRANGE #
        step_recorder = ListRecorder()
        recording_atc = ActionToCheckWrapperThatRecordsSteps(step_recorder,
                                                             _atc_that_does_nothing())
        actor = ActorForConstantAtc(
            recording_atc,
            parse_atc=do_raise(ValueError('failure message'))
        )
        arrangement = Arrangement(test_case=_empty_test_case(),
                                  actor=actor)
        # ASSERT #
        expectation = Expectation(phase_result=asrt_result.status_is(ExecutionFailureStatus.INTERNAL_ERROR))
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

    def test_WHEN_stdin_is_set_THEN_it_SHOULD_be_passed_to_the_atc(self):
        file_with_stdin_contents = fs.File('redirected-to-stdin.txt', 'contents of file to redirect')
        with tmp_dir(fs.DirContents([file_with_stdin_contents])) as abs_tmp_dir_path:
            absolute_name_of_file_to_redirect = abs_tmp_dir_path / file_with_stdin_contents.name
            setup_settings = StandardSetupSettingsHandler.new_empty()
            setup_settings.builder.stdin = ConstantAdvWValidation.new_wo_validation(
                file_source.string_source_of_file__poorly_described(
                    absolute_name_of_file_to_redirect,
                    DirFileSpaceThatMustNoBeUsed())
            )
            _check_contents_of_stdin_for_setup_settings(self,
                                                        setup_settings,
                                                        file_with_stdin_contents.contents)

    def test_WHEN_stdin_is_not_set_in_setup_THEN_it_should_be_empty(self):
        setup_settings = StandardSetupSettingsHandler.new_empty()
        setup_settings.stdin = None
        expected_contents_of_stdin = ''
        _check_contents_of_stdin_for_setup_settings(self,
                                                    setup_settings,
                                                    expected_contents_of_stdin)


def _exit_code_result_file_contains(expected_contents: str) -> Assertion:
    return asrt.sub_component('file for exit code',
                              lambda sds: sds.result.exitcode_file,
                              fa.path_is_file_with_contents(expected_contents))


def _stdout_result_file_contains(expected_contents: str) -> Assertion:
    return asrt.sub_component('file for stdout',
                              lambda sds: sds.result.stdout_file,
                              fa.path_is_file_with_contents(expected_contents))


def _stderr_result_file_contains(expected_contents: str) -> Assertion:
    return asrt.sub_component('file for stderr',
                              lambda sds: sds.result.stderr_file,
                              fa.path_is_file_with_contents(expected_contents))


def _check_contents_of_stdin_for_setup_settings(put: unittest.TestCase,
                                                settings_handler: SetupSettingsHandler,
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
            result = _execute(parser, test_case, settings_handler)
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
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        self.cwd_registerer.register_cwd_for(phase_step.ACT__PREPARE)
        return sh.new_sh_success()

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                input_: ActExecutionInput,
                output_files: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        self.cwd_registerer.register_cwd_for(phase_step.ACT__EXECUTE)
        return new_eh_exit_code(0)

    @property
    def actual_sds(self) -> SandboxDs:
        return self._actual_sds


class _AtcThatExecutesPythonProgramFile(ActionToCheckThatJustReturnsSuccess):
    def __init__(self, python_program_file: pathlib.Path):
        self.python_program_file = python_program_file

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                input_: ActExecutionInput,
                output: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        with as_stdin.of_optional(input_.stdin) as stdin_f:
            exit_code = subprocess.call([sys.executable, str(self.python_program_file)],
                                        timeout=60,
                                        stdin=stdin_f,
                                        stdout=output.out,
                                        stderr=output.err)
            return new_eh_exit_code(exit_code)


class _AtcThatReturnsConstantExitCode(ActionToCheckThatJustReturnsSuccess):
    def __init__(self, exit_code: int):
        self.exit_code = exit_code

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                input_: ActExecutionInput,
                output: StdOutputFiles,
                ) -> ExitCodeOrHardError:
        return new_eh_exit_code(self.exit_code)


def _empty_test_case() -> TestCase:
    return TestCase(new_empty_section_contents(),
                    new_empty_section_contents(),
                    new_empty_section_contents(),
                    new_empty_section_contents(),
                    new_empty_section_contents())


def _execute(actor: Actor,
             test_case: TestCase,
             setup_settings_handler: Optional[SetupSettingsHandler] = None,
             is_keep_sandbox: bool = False,
             current_directory: pathlib.Path = None,
             mem_buff_size: int = 2 ** 10,
             ) -> PartialExeResult:
    if current_directory is None:
        current_directory = pathlib.Path.cwd()
    with home_directory_structure() as hds:
        with preserved_cwd():
            os.chdir(str(current_directory))
            return sut.execute(
                test_case,
                ExecutionConfiguration(dict(os.environ),
                                       os_services_access.new_for_current_os(),
                                       sandbox_root_name_resolver.for_test(),
                                       mem_buff_size),
                ConfPhaseValues(NameAndValue('the actor', actor),
                                hds),
                settings_handlers.from_optional(setup_settings_handler),
                is_keep_sandbox)


def _python_program_that_prints_stdin_to(output_file_path: pathlib.Path) -> str:
    return _PYTHON_PROGRAM_THAT_PRINTS_STDIN_TO_FILE_NAME.format(file_name=str(output_file_path))


def _atc_that_does_nothing() -> ActionToCheck:
    return ActionToCheckThatRunsConstantActions()


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
