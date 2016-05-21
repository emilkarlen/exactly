import os
import pathlib
import random
import unittest
from contextlib import contextmanager

from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents
from exactly_lib_test.test_resources.execution.utils import execution_directory_structure
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir
from exactly_lib_test.test_resources.process import ProcessExecutor, SubProcessResult
from exactly_lib_test.test_resources.process import capture_process_executor_result


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
        return self.program_executor.execute(self.source_setup,
                                             self.home_dir_path,
                                             self.eds,
                                             files)


class TestBase(unittest.TestCase):
    def __init__(self, test_setup: Configuration):
        super().__init__()
        self.test_setup = test_setup

    def _execute(self,
                 source: ActSourceBuilder,
                 stdin_contents: str = '') -> SubProcessResult:
        act_program_executor = self.test_setup.sut
        home_dir = pathlib.Path()
        validation_result = act_program_executor.validate(home_dir, source)
        self.assertEqual(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                         validation_result.status)
        with execution_directory_structure() as eds:
            program_setup = SourceSetup(source,
                                        eds.test_case_dir,
                                        'file-name-stem')
            act_program_executor.prepare(program_setup, home_dir, eds)
            process_executor = _ProcessExecutorForProgramExecutor(program_setup,
                                                                  home_dir,
                                                                  eds,
                                                                  act_program_executor)
            return capture_process_executor_result(process_executor,
                                                   eds.result.root_dir,
                                                   stdin_contents=stdin_contents)


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
                                                eds.test_case_dir,
                                                'file-name-stem')
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
