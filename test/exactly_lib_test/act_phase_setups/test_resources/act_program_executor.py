import os
import pathlib
import random
import unittest
from contextlib import contextmanager

from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor, ExitCodeOrHardError
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles, std_files_dev_null
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.instructions.test_resources import sh_check__va as sh_check
from exactly_lib_test.test_resources import value_assertion as va
from exactly_lib_test.test_resources.execution import eds_contents_check
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.utils import execution_directory_structure
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.process import ProcessExecutor, SubProcessResult
from exactly_lib_test.test_resources.process import capture_process_executor_result
from exactly_lib_test.test_resources.value_assertion import MessageBuilder


class Configuration:
    def __init__(self, sut: ActSourceExecutor):
        self.sut = sut

    @contextmanager
    def program_that_copes_stdin_to_stdout(self) -> ActSourceBuilder:
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stdout(self, string_to_print: str) -> ActSourceBuilder:
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_to_stderr(self, string_to_print: str) -> ActSourceBuilder:
        raise NotImplementedError()

    @contextmanager
    def program_that_exits_with_code(self, exit_code: int) -> ActSourceBuilder:
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self) -> ActSourceBuilder:
        raise NotImplementedError()

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ActSourceBuilder:
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


class _ProcessExecutorForProgramExecutor(ProcessExecutor):
    def __init__(self,
                 source_setup: SourceSetup,
                 home_dir_path: pathlib.Path,
                 eds: ExecutionDirectoryStructure,
                 program_executor: ActSourceExecutor):
        self.program_executor = program_executor
        self.source_setup = source_setup
        self.home_dir_path = home_dir_path
        self.eds = eds

    def execute(self,
                files: StdFiles) -> int:
        exit_code_or_hard_error = self.program_executor.execute(self.source_setup,
                                                                self.home_dir_path,
                                                                self.eds,
                                                                files)
        if exit_code_or_hard_error.is_exit_code:
            return exit_code_or_hard_error.exit_code
        msg = '%s returned HARD ERROR: %s' % (str(ActSourceExecutor),
                                              str(exit_code_or_hard_error.failure_details))
        raise ValueError(msg)


class TestWithActSourceExecutorBase(unittest.TestCase):
    def __init__(self, act_source_executor: ActSourceExecutor):
        super().__init__()
        self.act_source_executor = act_source_executor

    def _execute(self,
                 source: ActSourceBuilder,
                 stdin_contents: str = '') -> SubProcessResult:
        act_program_executor = self.act_source_executor
        home_dir = pathlib.Path()
        validation_result = act_program_executor.validate(home_dir, source)
        self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                         validation_result.status)
        with execution_directory_structure() as eds:
            program_setup = SourceSetup(source,
                                        eds.test_case_dir)
            act_program_executor.prepare(program_setup, home_dir, eds)
            process_executor = _ProcessExecutorForProgramExecutor(program_setup,
                                                                  home_dir,
                                                                  eds,
                                                                  act_program_executor)
            return capture_process_executor_result(process_executor,
                                                   eds.result.root_dir,
                                                   stdin_contents=stdin_contents)


class Arrangement:
    def __init__(self,
                 executor: ActSourceExecutor,
                 source: ActSourceBuilder):
        self.executor = executor
        self.source = source


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


def check_execution(put: unittest.TestCase,
                    arrangement: Arrangement,
                    expectation: Expectation) -> ExitCodeOrHardError:
    home_dir = pathlib.Path()
    validation_result = arrangement.executor.validate(home_dir, arrangement.source)
    put.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                    validation_result.status)
    with execution_directory_structure() as eds:
        program_setup = SourceSetup(arrangement.source,
                                    eds.test_case_dir)
        actual = arrangement.executor.prepare(program_setup, home_dir, eds)
        expectation.side_effects_on_files_after_prepare.apply(put, eds)
        expectation.result_of_prepare.apply(put, actual,
                                            MessageBuilder('Result of prepare'))
        if not actual.is_success:
            return
        actual = arrangement.executor.execute(program_setup, home_dir, eds, std_files_dev_null())
        expectation.result_of_execute.apply(put, actual,
                                            MessageBuilder('Result of execute'))
        expectation.side_effects_on_files_after_execute.apply(put, eds)
        return actual


class TestBase(TestWithActSourceExecutorBase):
    def __init__(self, test_setup: Configuration):
        super().__init__(test_setup.sut)
        self.test_setup = test_setup


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
                act_program_executor = self.test_setup.sut
                home_dir = pathlib.Path.cwd()
                validation_result = act_program_executor.validate(home_dir, source)
                self.assertEqual(svh.new_svh_success(),
                                 validation_result)
                with execution_directory_structure(act_dir_contents(DirContents([empty_dir('expected-cwd')]))) as eds:
                    program_setup = SourceSetup(source,
                                                eds.test_case_dir)
                    process_cwd = str(eds.act_dir / 'expected-cwd')
                    os.chdir(process_cwd)
                    assert process_cwd == os.getcwd()
                    act_program_executor.prepare(program_setup, home_dir, eds)
                    process_executor = _ProcessExecutorForProgramExecutor(program_setup,
                                                                          home_dir,
                                                                          eds,
                                                                          act_program_executor)
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
