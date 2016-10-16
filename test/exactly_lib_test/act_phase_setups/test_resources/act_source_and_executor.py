import os
import pathlib
import random
import unittest
from contextlib import contextmanager

from exactly_lib.execution.act_phase import ActSourceExecutor, ExitCodeOrHardError, \
    ActSourceAndExecutorConstructor, ActSourceAndExecutor
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep, HomeAndEds
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles, std_files_dev_null
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.instructions.test_resources import sh_check__va as sh_check
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources import file_structure_utils as fs_utils
from exactly_lib_test.test_resources.execution import eds_contents_check
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.utils import execution_directory_structure
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.process import ProcessExecutor, SubProcessResult
from exactly_lib_test.test_resources.process import capture_process_executor_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


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


def suite_for_execution(setup: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(setup) for tcc in
                              [TestStdoutIsConnectedToProgram,
                               TestStderrIsConnectedToProgram,
                               TestStdinAndStdoutAreConnectedToProgram,
                               TestExitCodeIsReturned,
                               TestEnvironmentVariablesAreAccessibleByProgram,
                               TestInitialCwdIsCurrentDirAndThatCwdIsRestoredAfterwards,
                               ])


class _ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(ProcessExecutor):
    def __init__(self,
                 home_and_eds: HomeAndEds,
                 script_output_path: pathlib.Path,
                 program_executor: ActSourceAndExecutor):
        self.program_executor = program_executor
        self.home_and_eds = home_and_eds
        self.script_output_path = script_output_path

    def execute(self,
                files: StdFiles) -> int:
        exit_code_or_hard_error = self.program_executor.execute(self.home_and_eds,
                                                                self.script_output_path,
                                                                files)
        if exit_code_or_hard_error.is_exit_code:
            return exit_code_or_hard_error.exit_code
        msg = '%s returned HARD ERROR: %s' % (str(ActSourceExecutor),
                                              str(exit_code_or_hard_error.failure_details))
        raise ValueError(msg)


class TestExecuteBase(unittest.TestCase):
    def __init__(self, source_and_executor_constructor: ActSourceAndExecutorConstructor):
        super().__init__()
        self.source_and_executor_constructor = source_and_executor_constructor

    def _execute(self,
                 act_phase_instructions: list,
                 stdin_contents: str = '') -> SubProcessResult:
        _assert_is_list_of_act_phase_instructions(self, act_phase_instructions)

        cwd_before_test = os.getcwd()
        home_dir = pathlib.Path()
        environment = GlobalEnvironmentForPreEdsStep(home_dir)
        sut = self.source_and_executor_constructor.apply(environment, act_phase_instructions)
        step_result = sut.validate_pre_eds(home_dir)
        self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                         step_result.status,
                         'Result of validation/pre-eds')
        with execution_directory_structure() as eds:
            try:
                os.chdir(str(eds.act_dir))
                home_and_eds = HomeAndEds(home_dir, eds)
                step_result = sut.validate_post_setup(home_and_eds)
                self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                 step_result.status,
                                 'Result of validation/post-setup')
                script_output_path = eds.test_case_dir
                step_result = sut.prepare(home_and_eds, script_output_path)
                self.assertTrue(step_result.is_success,
                                'Expecting success from prepare (found hard error)')
                process_executor = _ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(home_and_eds,
                                                                                                     script_output_path,
                                                                                                     sut)
                return capture_process_executor_result(process_executor,
                                                       eds.result.root_dir,
                                                       stdin_contents=stdin_contents)
            finally:
                os.chdir(cwd_before_test)


class Arrangement:
    def __init__(self,
                 executor_constructor: ActSourceAndExecutorConstructor,
                 act_phase_instructions: list,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 ):
        self.executor_constructor = executor_constructor
        self.act_phase_instructions = act_phase_instructions
        self.home_dir_contents = home_dir_contents


class Expectation:
    def __init__(self,
                 side_effects_on_files_after_execute: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 side_effects_on_files_after_prepare: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 result_of_prepare: va.ValueAssertion = sh_check.is_success(),
                 result_of_execute: va.ValueAssertion = eh_check.is_any_exit_code):
        self.side_effects_on_files_after_prepare = side_effects_on_files_after_prepare
        self.side_effects_on_files_after_execute = side_effects_on_files_after_execute
        self.result_of_prepare = result_of_prepare
        self.result_of_execute = result_of_execute


def simple_success() -> Expectation:
    return Expectation()


def check_execution(put: unittest.TestCase,
                    arrangement: Arrangement,
                    expectation: Expectation) -> ExitCodeOrHardError:
    _assert_is_list_of_act_phase_instructions(put, arrangement.act_phase_instructions)

    cwd_before_test = os.getcwd()
    with fs_utils.tmp_dir(arrangement.home_dir_contents) as home_dir:
        environment = GlobalEnvironmentForPreEdsStep(home_dir)
        sut = arrangement.executor_constructor.apply(environment, arrangement.act_phase_instructions)
        step_result = sut.validate_pre_eds(home_dir)
        put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                        step_result.status,
                        'Result of validation/pre-eds')
        with execution_directory_structure() as eds:
            try:
                os.chdir(str(eds.act_dir))
                home_and_eds = HomeAndEds(home_dir, eds)
                step_result = sut.validate_post_setup(home_and_eds)
                put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                step_result.status,
                                'Result of validation/post-setup')
                script_output_dir_path = eds.test_case_dir
                step_result = sut.prepare(home_and_eds, script_output_dir_path)
                expectation.side_effects_on_files_after_prepare.apply(put, eds)
                expectation.result_of_prepare.apply(put,
                                                    step_result,
                                                    MessageBuilder('Result of prepare'))
                if not step_result.is_success:
                    return
                step_result = sut.execute(home_and_eds, script_output_dir_path, std_files_dev_null())
                if step_result.is_hard_error:
                    error_msg_extra_info = os.linesep + str(step_result.failure_details) + os.linesep
                else:
                    error_msg_extra_info = ''
                expectation.result_of_execute.apply(put,
                                                    step_result,
                                                    MessageBuilder('Result of execute' + error_msg_extra_info))
                expectation.side_effects_on_files_after_execute.apply(put, eds)
                return step_result
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
                environment = GlobalEnvironmentForPreEdsStep(home_dir)
                sut = executor_constructor.apply(environment, source)
                step_result = sut.validate_pre_eds(home_dir)
                self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                 step_result.status,
                                 'Result of validation/pre-eds')
                with execution_directory_structure(act_dir_contents(DirContents([empty_dir('expected-cwd')]))) as eds:
                    home_and_eds = HomeAndEds(home_dir, eds)
                    process_cwd = str(eds.act_dir / 'expected-cwd')
                    os.chdir(process_cwd)
                    assert process_cwd == os.getcwd()
                    step_result = sut.validate_post_setup(home_and_eds)
                    self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                                     step_result.status,
                                     'Result of validation/post-setup')
                    script_output_dir_path = eds.test_case_dir
                    step_result = sut.prepare(home_and_eds, script_output_dir_path)
                    self.assertTrue(step_result.is_success,
                                    'Expecting success from prepare (found hard error)')
                    process_executor = _ProcessExecutorForProgramExecutorThatRaisesIfResultIsNotExitCode(home_and_eds,
                                                                                                         script_output_dir_path,
                                                                                                         sut)
                    process_result = capture_process_executor_result(process_executor,
                                                                     eds.result.root_dir)
                    self.assertEqual(process_cwd,
                                     process_result.stdout,
                                     'Current Working Directory for program should be act-directory')

                    self.assertEqual(process_cwd,
                                     os.getcwd(),
                                     'Current Working Directory should be restored after program has finished')
        finally:
            os.chdir(cwd_before)


def _assert_is_list_of_act_phase_instructions(put: unittest.TestCase, x):
    put.assertIsInstance(x, list,
                         'Invalid test input: Expecting list of ActPhaseInstruction:s. Found: ' + str(type(x)))
    i = 0
    for e in x:
        put.assertIsInstance(e, ActPhaseInstruction,
                             'Invalid test input: Element [%d]. Expecting an ActPhaseInstruction:s. Found: %s' %
                             (i, type(e)))
        i += 1
