import pathlib
import subprocess
import sys
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution as sut
from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.act_phase import ActSourceAndExecutor, ExitCodeOrHardError, new_eh_exit_code, \
    ActPhaseHandling, ActSourceAndExecutorConstructor
from exactly_lib.section_document.model import new_empty_section_contents
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.partial_execution.test_resources.arrange_and_expect import execute_and_check, \
    Arrangement, Expectation
from exactly_lib_test.execution.test_resources.execution_recording.act_program_executor import \
    ActSourceAndExecutorConstructorForConstantExecutor, ActSourceAndExecutorThatJustReturnsSuccess
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_checks import FileChecker
from exactly_lib_test.test_resources.file_structure_utils import tmp_dir, preserved_cwd
from exactly_lib_test.test_resources.value_assertions import file_assertions as fa
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCurrentDirectory),
        unittest.makeSuite(TestExecute),
    ])


class TestCurrentDirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE
        executor_that_records_current_dir = _ExecutorThatRecordsCurrentDir()
        constructor = ActSourceAndExecutorConstructorForConstantExecutor(executor_that_records_current_dir)
        # ACT #
        _execute(constructor, _empty_test_case())
        # ASSERT #
        phase_step_2_cwd = executor_that_records_current_dir.phase_step_2_cwd
        home_and_eds = executor_that_records_current_dir.actual_home_and_eds
        eds = home_and_eds.eds
        self.assertEqual(len(phase_step_2_cwd),
                         4,
                         'Expects recordings for 4 steps')
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__VALIDATE_PRE_EDS],
                         str(home_and_eds.home_dir_path),
                         'Current dir for ' + str(phase_step.ACT__VALIDATE_PRE_EDS))
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__VALIDATE_POST_SETUP],
                         str(eds.act_dir),
                         'Current dir for ' + str(phase_step.ACT__VALIDATE_POST_SETUP))
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__PREPARE],
                         str(eds.act_dir),
                         'Current dir for ' + str(phase_step.ACT__PREPARE))
        self.assertEqual(phase_step_2_cwd[phase_step.ACT__EXECUTE],
                         str(eds.act_dir),
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
            setup_settings.stdin.file_name = str(absolute_name_of_file_to_redirect)
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


def _exit_code_result_file_contains(expected_contents: str) -> va.ValueAssertion:
    return va.sub_component('file for exit code',
                            lambda sds: sds.result.exitcode_file,
                            fa.PathIsFileWithContents(expected_contents))


def _stdout_result_file_contains(expected_contents: str) -> va.ValueAssertion:
    return va.sub_component('file for stdout',
                            lambda sds: sds.result.stdout_file,
                            fa.PathIsFileWithContents(expected_contents))


def _stderr_result_file_contains(expected_contents: str) -> va.ValueAssertion:
    return va.sub_component('file for stderr',
                            lambda sds: sds.result.stderr_file,
                            fa.PathIsFileWithContents(expected_contents))


def _check_contents_of_stdin_for_setup_settings(put: unittest.TestCase,
                                                setup_settings: SetupSettingsBuilder,
                                                expected_contents_of_stdin: str,
                                                home_dir_path: pathlib.Path = pathlib.Path().resolve()) -> sut.PartialResult:
    """
    Tests contents of stdin by executing a Python program that stores
    the contents of stdin in a file.
    """
    with preserved_cwd():
        with tmp_dir() as tmp_dir_path:
            # ARRANGE #
            output_file_path = tmp_dir_path / 'output.txt'
            python_program_file = fs.File('program.py', _python_program_that_prints_stdin_to(output_file_path))
            python_program_file.write_to(tmp_dir_path)
            executor_that_records_contents_of_stdin = _ExecutorThatExecutesPythonProgramFile(
                tmp_dir_path / 'program.py')
            constructor = ActSourceAndExecutorConstructorForConstantExecutor(executor_that_records_contents_of_stdin)
            test_case = _empty_test_case()
            # ACT #
            result = _execute(constructor, test_case, setup_settings, home_dir_path=home_dir_path)
            # ASSERT #
            file_checker = FileChecker(put)
            file_checker.assert_file_contents(output_file_path,
                                              expected_contents_of_stdin)
            return result


class _ExecutorThatRecordsCurrentDir(ActSourceAndExecutor):
    def __init__(self):
        self._home_and_eds = None
        self.phase_step_2_cwd = {}

    def validate_pre_eds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        self._register_cwd_for(phase_step.ACT__VALIDATE_PRE_EDS)
        return svh.new_svh_success()

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        self._home_and_eds = home_and_eds
        self._register_cwd_for(phase_step.ACT__VALIDATE_POST_SETUP)
        return svh.new_svh_success()

    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self._register_cwd_for(phase_step.ACT__PREPARE)
        return sh.new_sh_success()

    def execute(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self._register_cwd_for(phase_step.ACT__EXECUTE)
        return new_eh_exit_code(0)

    def _register_cwd_for(self, step):
        self.phase_step_2_cwd[step] = str(pathlib.Path().resolve())

    @property
    def actual_home_and_eds(self) -> HomeAndEds:
        return self._home_and_eds


class _ExecutorThatExecutesPythonProgramFile(ActSourceAndExecutorThatJustReturnsSuccess):
    def __init__(self, python_program_file: pathlib.Path):
        self.python_program_file = python_program_file

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        exit_code = subprocess.call([sys.executable, str(self.python_program_file)],
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)


class _ExecutorThatExecutesPythonProgramSource(ActSourceAndExecutorThatJustReturnsSuccess):
    PYTHON_FILE_NAME = 'program.py'

    def __init__(self, python_program_source: str):
        self.python_program_source = python_program_source

    def execute(self,
                home_and_eds: HomeAndEds,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        python_file = pathlib.Path() / self.PYTHON_FILE_NAME
        with python_file.open(mode='w') as f:
            f.write(self.python_program_source)

        exit_code = subprocess.call([sys.executable, str(python_file)],
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
                home_and_eds: HomeAndEds,
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
             is_keep_execution_directory_root: bool = False,
             home_dir_path: pathlib.Path = pathlib.Path().resolve()) -> sut.PartialResult:
    return sut.execute(
        ActPhaseHandling(constructor),
        test_case,
        sut.Configuration(home_dir_path),
        setup_settings,
        program_info.PROGRAM_NAME + '-test-',
        is_keep_execution_directory_root)


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
