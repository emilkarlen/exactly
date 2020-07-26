import os
import random
import unittest
from contextlib import contextmanager
from typing import List

from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.atc_os_proc_executors import DEFAULT_ATC_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelHdsOptionType
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.simple_textstruct.file_printer_output import to_string
from exactly_lib_test.actors.test_resources import integration_check
from exactly_lib_test.actors.test_resources.integration_check import \
    ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode
from exactly_lib_test.actors.test_resources.misc import assert_is_list_of_act_phase_instructions
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import contents_in
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents, Dir
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.process import capture_process_executor_result
from exactly_lib_test.test_resources.tcds_and_symbols.sds_env_utils import sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class TestCaseSourceSetup:
    def __init__(self, act_phase_instructions: List[ActPhaseInstruction],
                 home_act_dir_contents: DirContents = empty_dir_contents(),
                 ):
        self.home_act_dir_contents = home_act_dir_contents
        self.act_phase_instructions = act_phase_instructions


class Configuration:
    def __init__(self, sut: Actor):
        self.sut = sut

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, hds: HomeDirectoryStructure) -> List[ActPhaseInstruction]:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stdout(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> List[ActPhaseInstruction]:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stderr(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> List[ActPhaseInstruction]:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_exits_with_code(self,
                                     hds: HomeDirectoryStructure,
                                     exit_code: int) -> List[ActPhaseInstruction]:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self,
                                                           hds: HomeDirectoryStructure) -> List[ActPhaseInstruction]:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self,
                                                                    hds: HomeDirectoryStructure,
                                                                    var_name: str) -> List[ActPhaseInstruction]:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        raise NotImplementedError()


def suite_for_execution(setup: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(setup) for tcc in
                              [TestStdoutIsConnectedToProgram,
                               TestStderrIsConnectedToProgram,
                               TestStdinAndStdoutAreConnectedToProgram,
                               TestExitCodeIsReturned,
                               TestEnvironmentVariablesAreAccessibleByProgram,
                               TestInitialCwdIsCurrentDirAndThatCwdIsRestoredAfterwards,
                               TestTimeoutValueIsUsed,
                               ])


class TestExecuteBase(unittest.TestCase):
    def __init__(self, actor: Actor):
        super().__init__()
        self.actor = actor

    def _execute__w_spr_check(self,
                              hds: HomeDirectoryStructure,
                              instructions: List[ActPhaseInstruction],
                              stdin_contents: str = '',
                              environ: dict = None,
                              execute_output: ValueAssertion[SubProcessResult] = asrt.anything_goes(),
                              ):
        result_from_execute = self._execute(
            hds,
            instructions,
            stdin_contents,
            environ
        )
        execute_output.apply_with_message(
            self,
            result_from_execute,
            'result from execute'
        )

    def _execute(self,
                 hds: HomeDirectoryStructure,
                 act_phase_instructions: List[ActPhaseInstruction],
                 stdin_contents: str = '',
                 environ: dict = None) -> SubProcessResult:
        environ = {} if environ is None else environ
        assert_is_list_of_act_phase_instructions(self, act_phase_instructions)

        environment = InstructionEnvironmentForPreSdsStep(
            hds,
            ProcessExecutionSettings.with_environ(environ),
        )
        sut = self.actor.parse(act_phase_instructions)
        step_result = sut.validate_pre_sds(environment)
        if step_result.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            self.fail('Expecting success. Found {}: {}'.format(
                step_result.status,
                to_string.major_blocks(step_result.failure_message.render()),
            ))
        with sds_with_act_as_curr_dir() as path_resolving_env:
            environment_builder = InstructionEnvironmentPostSdsBuilder.new_from_pre_sds(
                environment,
                path_resolving_env.sds,
            )
            environment = environment_builder.build_post_sds()

            step_result = sut.validate_post_setup(environment)
            self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                             step_result.status,
                             'Result of validation/post-setup')
            step_result = sut.prepare(environment, DEFAULT_ATC_OS_PROCESS_EXECUTOR)
            self.assertTrue(step_result.is_success,
                            'Expecting success from prepare (found hard error)')
            process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(
                environment,
                DEFAULT_ATC_OS_PROCESS_EXECUTOR,
                sut)
            return capture_process_executor_result(process_executor,
                                                   path_resolving_env.sds.result.root_dir,
                                                   stdin_contents=stdin_contents)


class TestBase(TestExecuteBase):
    def __init__(self, test_setup: Configuration):
        super().__init__(test_setup.sut)
        self.test_setup = test_setup

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.test_setup))


class TestStdoutIsConnectedToProgram(TestBase):
    def runTest(self):
        with home_directory_structure() as hds:
            with self.test_setup.program_that_prints_to_stdout(
                    hds,
                    'expected output on stdout') as program:
                self._execute__w_spr_check(
                    hds,
                    program,
                    execute_output=asrt_proc_result.matches_proc_result(
                        stdout=asrt.equals('expected output on stdout\n')
                    )
                )


class TestStderrIsConnectedToProgram(TestBase):
    def runTest(self):
        with home_directory_structure() as hds:
            with self.test_setup.program_that_prints_to_stderr(hds,
                                                               'expected output on stderr') as program:
                self._execute__w_spr_check(
                    hds,
                    program,
                    execute_output=asrt_proc_result.matches_proc_result(
                        stderr=asrt.equals('expected output on stderr\n')
                    )
                )


class TestStdinAndStdoutAreConnectedToProgram(TestBase):
    def runTest(self):
        with home_directory_structure() as hds:
            with self.test_setup.program_that_copes_stdin_to_stdout(hds) as program:
                self._execute__w_spr_check(
                    hds,
                    program,
                    stdin_contents='contents of stdin',
                    execute_output=asrt_proc_result.matches_proc_result(
                        stdout=asrt.equals('contents of stdin')
                    )
                )


class TestExitCodeIsReturned(TestBase):
    def runTest(self):
        with home_directory_structure() as hds:
            with self.test_setup.program_that_exits_with_code(hds, 87) as program:
                self._execute__w_spr_check(
                    hds,
                    program,
                    stdin_contents='contents of stdin',
                    execute_output=asrt_proc_result.matches_proc_result(
                        exit_code=asrt.equals(87)
                    )
                )


class TestEnvironmentVariablesAreAccessibleByProgram(TestBase):
    def runTest(self):
        var_name = 'THIS_IS_A_TEST_VAR_23026509234'
        var_value = str(random.getrandbits(32))
        environ = dict(os.environ)
        environ[var_name] = var_value
        with home_directory_structure() as hds:
            with self.test_setup.program_that_prints_value_of_environment_variable_to_stdout(
                    hds,
                    var_name) as program:
                self._execute__w_spr_check(
                    hds,
                    program,
                    environ=environ,
                    execute_output=asrt_proc_result.matches_proc_result(
                        stdout=asrt.equals(var_value + '\n')
                    )
                )


class TestInitialCwdIsCurrentDirAndThatCwdIsRestoredAfterwards(TestBase):
    def runTest(self):
        with home_directory_structure() as hds:
            with self.test_setup.program_that_prints_cwd_without_new_line_to_stdout(hds) as source:
                executor_constructor = self.test_setup.sut
                environment = InstructionEnvironmentForPreSdsStep(
                    hds,
                    ProcessExecutionSettings.with_empty_environ(),
                )
                sut = executor_constructor.parse(source)
                step_result = sut.validate_pre_sds(environment)
                self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                 step_result.status,
                                 'Result of validation/pre-sds')
                with sds_with_act_as_curr_dir(contents_in(RelSdsOptionType.REL_ACT,
                                                          DirContents([Dir.empty('expected-cwd')]))
                                              ) as path_resolving_env:
                    environment_builder = InstructionEnvironmentPostSdsBuilder.new_from_pre_sds(
                        environment,
                        path_resolving_env.sds,
                    )
                    environment = environment_builder.build_post_sds()

                    process_cwd = str(path_resolving_env.sds.act_dir / 'expected-cwd')
                    os.chdir(process_cwd)
                    assert process_cwd == os.getcwd()
                    step_result = sut.validate_post_setup(environment)
                    self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     step_result.status,
                                     'Result of validation/post-setup')
                    step_result = sut.prepare(environment,
                                              DEFAULT_ATC_OS_PROCESS_EXECUTOR)
                    self.assertTrue(step_result.is_success,
                                    'Expecting success from prepare (found hard error)')
                    process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(
                        environment,
                        DEFAULT_ATC_OS_PROCESS_EXECUTOR,
                        sut)
                    process_result = capture_process_executor_result(process_executor,
                                                                     path_resolving_env.sds.result.root_dir)
                    self.assertEqual(process_cwd + '\n',
                                     process_result.stdout,
                                     'Current Working Directory for program should be act-directory')

                    self.assertEqual(process_cwd,
                                     os.getcwd(),
                                     'Current Working Directory should be restored after program has finished')


class TestTimeoutValueIsUsed(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        with self.configuration.program_that_sleeps_at_least(5) as test_case_setup:
            arrangement = integration_check.Arrangement(
                hds_contents=hds_populators.contents_in(RelHdsOptionType.REL_HDS_ACT,
                                                        test_case_setup.home_act_dir_contents),
                process_execution=ProcessExecutionArrangement(
                    process_execution_settings=ProcessExecutionSettings(
                        timeout_in_seconds=1
                    )
                ))
            expectation = integration_check.Expectation(execute=eh_assertions.is_hard_error)
            integration_check.check_execution(self,
                                              self.configuration.sut,
                                              test_case_setup.act_phase_instructions,
                                              arrangement,
                                              expectation)
