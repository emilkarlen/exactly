import os
import pathlib
import random
import unittest
from contextlib import contextmanager

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import \
    assert_is_list_of_act_phase_instructions, ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_env_utils import sds_with_act_as_curr_dir
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.process import capture_process_executor_result


class TestCaseSourceSetup:
    def __init__(self, act_phase_instructions: list,
                 home_dir_contents: DirContents = DirContents([])):
        self.home_dir_contents = home_dir_contents
        self.act_phase_instructions = act_phase_instructions


class Configuration:
    def __init__(self, sut: ActSourceAndExecutorConstructor):
        self.sut = sut

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stdout(self,
                                      home_dir_path: pathlib.Path,
                                      string_to_print: str) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stderr(self,
                                      home_dir_path: pathlib.Path,
                                      string_to_print: str) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_exits_with_code(self,
                                     home_dir_path: pathlib.Path,
                                     exit_code: int) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self,
                                                                    home_dir_path: pathlib.Path,
                                                                    var_name: str) -> list:
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
    def __init__(self, source_and_executor_constructor: ActSourceAndExecutorConstructor):
        super().__init__()
        self.source_and_executor_constructor = source_and_executor_constructor

    def _execute(self,
                 home_dir: pathlib.Path,
                 act_phase_instructions: list,
                 stdin_contents: str = '',
                 environ: dict = None) -> SubProcessResult:
        environ = dict(os.environ) if environ is None else environ
        assert_is_list_of_act_phase_instructions(self, act_phase_instructions)

        environment = InstructionEnvironmentForPreSdsStep(home_dir, environ)
        sut = self.source_and_executor_constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR,
                                                         environment,
                                                         act_phase_instructions)
        step_result = sut.validate_pre_sds(environment)
        if step_result.status is not svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS:
            self.fail('Expecting success. Found {}: {}'.format(
                step_result.status,
                step_result.failure_message,
            ))
        with sds_with_act_as_curr_dir() as path_resolving_env:
            environment = InstructionEnvironmentForPostSdsStep(environment.home_directory,
                                                               environment.environ,
                                                               path_resolving_env.sds,
                                                               phase_identifier.ACT.identifier,
                                                               environment.timeout_in_seconds)
            step_result = sut.validate_post_setup(environment)
            self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                             step_result.status,
                             'Result of validation/post-setup')
            script_output_path = path_resolving_env.sds.test_case_dir
            step_result = sut.prepare(environment, script_output_path)
            self.assertTrue(step_result.is_success,
                            'Expecting success from prepare (found hard error)')
            process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(environment,
                                                                                                script_output_path,
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
        with tmp_dir() as home_dir_path:
            with self.test_setup.program_that_prints_to_stdout(home_dir_path,
                                                               'expected output on stdout') as program:
                process_result = self._execute(home_dir_path, program)
                self.assertEqual('expected output on stdout\n',
                                 process_result.stdout,
                                 'Contents of stdout')


class TestStderrIsConnectedToProgram(TestBase):
    def runTest(self):
        with tmp_dir() as home_dir_path:
            with self.test_setup.program_that_prints_to_stderr(home_dir_path,
                                                               'expected output on stderr') as program:
                process_result = self._execute(home_dir_path, program)
                self.assertEqual('expected output on stderr\n',
                                 process_result.stderr,
                                 'Contents of stderr')


class TestStdinAndStdoutAreConnectedToProgram(TestBase):
    def runTest(self):
        with tmp_dir() as home_dir_path:
            with self.test_setup.program_that_copes_stdin_to_stdout(home_dir_path) as program:
                process_result = self._execute(home_dir_path,
                                               program,
                                               stdin_contents='contents of stdin')
                self.assertEqual('contents of stdin',
                                 process_result.stdout,
                                 'Contents of stdout is expected to be equal to stdin')


class TestExitCodeIsReturned(TestBase):
    def runTest(self):
        with tmp_dir() as home_dir_path:
            with self.test_setup.program_that_exits_with_code(home_dir_path, 87) as program:
                process_result = self._execute(home_dir_path, program)
                self.assertEqual(87,
                                 process_result.exitcode,
                                 'Exit Code')


class TestEnvironmentVariablesAreAccessibleByProgram(TestBase):
    def runTest(self):
        var_name = 'THIS_IS_A_TEST_VAR_23026509234'
        var_value = str(random.getrandbits(32))
        environ = dict(os.environ)
        environ[var_name] = var_value
        with tmp_dir() as home_dir_path:
            with self.test_setup.program_that_prints_value_of_environment_variable_to_stdout(home_dir_path,
                                                                                             var_name) as program:
                process_result = self._execute(home_dir_path, program, environ=environ)
                self.assertEqual(var_value + '\n',
                                 process_result.stdout,
                                 'Contents of stdout should be value of environment variable')


class TestInitialCwdIsCurrentDirAndThatCwdIsRestoredAfterwards(TestBase):
    def runTest(self):
        with tmp_dir() as home_dir_path:
            with self.test_setup.program_that_prints_cwd_without_new_line_to_stdout(home_dir_path) as source:
                executor_constructor = self.test_setup.sut
                environment = InstructionEnvironmentForPreSdsStep(home_dir_path, dict(os.environ))
                sut = executor_constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, environment, source)
                step_result = sut.validate_pre_sds(environment)
                self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                 step_result.status,
                                 'Result of validation/pre-sds')
                with sds_with_act_as_curr_dir(act_dir_contents(DirContents([empty_dir('expected-cwd')]))
                                              ) as path_resolving_env:
                    environment = InstructionEnvironmentForPostSdsStep(environment.home_directory,
                                                                       environment.environ,
                                                                       path_resolving_env.sds,
                                                                       phase_identifier.ACT.identifier,
                                                                       environment.timeout_in_seconds)
                    process_cwd = str(path_resolving_env.sds.act_dir / 'expected-cwd')
                    os.chdir(process_cwd)
                    assert process_cwd == os.getcwd()
                    step_result = sut.validate_post_setup(environment)
                    self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     step_result.status,
                                     'Result of validation/post-setup')
                    script_output_dir_path = path_resolving_env.sds.test_case_dir
                    step_result = sut.prepare(environment, script_output_dir_path)
                    self.assertTrue(step_result.is_success,
                                    'Expecting success from prepare (found hard error)')
                    process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(
                        environment,
                        script_output_dir_path,
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
            arrangement = act_phase_execution.Arrangement(self.configuration.sut,
                                                          test_case_setup.act_phase_instructions,
                                                          home_dir_contents=test_case_setup.home_dir_contents,
                                                          timeout_in_seconds=1)
            expectation = act_phase_execution.Expectation(result_of_execute=eh_check.is_hard_error)
            act_phase_execution.check_execution(self, arrangement, expectation)
