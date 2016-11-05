import os
import pathlib
import random
import unittest
from contextlib import contextmanager

from exactly_lib.execution.act_phase import ActSourceAndExecutorConstructor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, HomeAndSds
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import \
    assert_is_list_of_act_phase_instructions, ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.utils import sandbox_directory_structure
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.process import capture_process_executor_result


class Configuration:
    def __init__(self, sut: ActSourceAndExecutorConstructor):
        self.sut = sut

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> list:
        """
        :return: List of ActPhaseInstruction
        """
        raise NotImplementedError()

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> list:
        """
        :return: List of ActPhaseInstruction
        """
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
                 act_phase_instructions: list,
                 stdin_contents: str = '') -> SubProcessResult:
        assert_is_list_of_act_phase_instructions(self, act_phase_instructions)

        cwd_before_test = os.getcwd()
        home_dir = pathlib.Path()
        environment = InstructionEnvironmentForPreSdsStep(home_dir)
        sut = self.source_and_executor_constructor.apply(environment, act_phase_instructions)
        step_result = sut.validate_pre_sds(home_dir)
        self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                         step_result.status,
                         'Result of validation/pre-sds')
        with sandbox_directory_structure() as sds:
            try:
                os.chdir(str(sds.act_dir))
                home_and_sds = HomeAndSds(home_dir, sds)
                step_result = sut.validate_post_setup(home_and_sds)
                self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                 step_result.status,
                                 'Result of validation/post-setup')
                script_output_path = sds.test_case_dir
                step_result = sut.prepare(home_and_sds, script_output_path)
                self.assertTrue(step_result.is_success,
                                'Expecting success from prepare (found hard error)')
                process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(home_and_sds,
                                                                                                    script_output_path,
                                                                                                    sut)
                return capture_process_executor_result(process_executor,
                                                       sds.result.root_dir,
                                                       stdin_contents=stdin_contents)
            finally:
                os.chdir(cwd_before_test)


class TestBase(TestExecuteBase):
    def __init__(self, test_setup: Configuration):
        super().__init__(test_setup.sut)
        self.test_setup = test_setup

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.test_setup))


class TestStdoutIsConnectedToProgram(TestBase):
    def runTest(self):
        with self.test_setup.program_that_prints_to_stdout('expected output on stdout') as program:
            process_result = self._execute(program)
            self.assertEqual('expected output on stdout',
                             process_result.stdout,
                             'Contents of stdout')


class TestStderrIsConnectedToProgram(TestBase):
    def runTest(self):
        with self.test_setup.program_that_prints_to_stderr('expected output on stderr') as program:
            process_result = self._execute(program)
            self.assertEqual('expected output on stderr',
                             process_result.stderr,
                             'Contents of stderr')


class TestStdinAndStdoutAreConnectedToProgram(TestBase):
    def runTest(self):
        with self.test_setup.program_that_copes_stdin_to_stdout() as program:
            process_result = self._execute(program,
                                           stdin_contents='contents of stdin')
            self.assertEqual('contents of stdin',
                             process_result.stdout,
                             'Contents of stdout is expected to be equal to stdin')


class TestExitCodeIsReturned(TestBase):
    def runTest(self):
        with self.test_setup.program_that_exits_with_code(87) as program:
            process_result = self._execute(program)
            self.assertEqual(87,
                             process_result.exitcode,
                             'Exit Code')


class TestEnvironmentVariablesAreAccessibleByProgram(TestBase):
    def runTest(self):
        var_name = 'THIS_IS_A_TEST_VAR_23026509234'
        var_value = str(random.getrandbits(32))
        os.environ[var_name] = var_value
        with self.test_setup.program_that_prints_value_of_environment_variable_to_stdout(var_name) as program:
            process_result = self._execute(program)
            self.assertEqual(var_value,
                             process_result.stdout,
                             'Contents of stdout should be value of environment variable')


class TestInitialCwdIsCurrentDirAndThatCwdIsRestoredAfterwards(TestBase):
    def runTest(self):
        cwd_before = os.getcwd()
        try:
            with self.test_setup.program_that_prints_cwd_without_new_line_to_stdout() as source:
                executor_constructor = self.test_setup.sut
                home_dir = pathlib.Path.cwd()
                environment = InstructionEnvironmentForPreSdsStep(home_dir)
                sut = executor_constructor.apply(environment, source)
                step_result = sut.validate_pre_sds(home_dir)
                self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                 step_result.status,
                                 'Result of validation/pre-sds')
                with sandbox_directory_structure(act_dir_contents(DirContents([empty_dir('expected-cwd')]))) as sds:
                    home_and_sds = HomeAndSds(home_dir, sds)
                    process_cwd = str(sds.act_dir / 'expected-cwd')
                    os.chdir(process_cwd)
                    assert process_cwd == os.getcwd()
                    step_result = sut.validate_post_setup(home_and_sds)
                    self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     step_result.status,
                                     'Result of validation/post-setup')
                    script_output_dir_path = sds.test_case_dir
                    step_result = sut.prepare(home_and_sds, script_output_dir_path)
                    self.assertTrue(step_result.is_success,
                                    'Expecting success from prepare (found hard error)')
                    process_executor = ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(home_and_sds,
                                                                                                        script_output_dir_path,
                                                                                                        sut)
                    process_result = capture_process_executor_result(process_executor,
                                                                     sds.result.root_dir)
                    self.assertEqual(process_cwd,
                                     process_result.stdout,
                                     'Current Working Directory for program should be act-directory')

                    self.assertEqual(process_cwd,
                                     os.getcwd(),
                                     'Current Working Directory should be restored after program has finished')
        finally:
            os.chdir(cwd_before)


class TestTimeoutValueIsUsed(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        with self.configuration.program_that_sleeps_at_least(5) as act_phase_instructions:
            arrangement = act_phase_execution.Arrangement(self.configuration.sut, act_phase_instructions,
                                                          timeout_in_seconds=1)
            expectation = act_phase_execution.Expectation(result_of_execute=eh_check.is_hard_error)
            act_phase_execution.check_execution(self, arrangement, expectation)
