import pathlib
import sys
import tempfile
import unittest

from shellcheck_lib.util.file_utils import resolved_path
from shellcheck_lib_test.cli.test_resources.execute_main_program import execute_main_program, \
    ARGUMENTS_FOR_TEST_INTERPRETER
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.run import run_shellcheck_in_sub_process
from shellcheck_lib_test.test_resources.file_structure import DirContents
from shellcheck_lib_test.test_resources.process import SubProcessResult


class SetupBase:
    def file_argument_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def check(self,
              put: unittest.TestCase,
              root_path: pathlib.Path,
              actual_result: SubProcessResult):
        raise NotImplementedError()


class SetupWithPreprocessor(SetupBase):
    """
    Setup that executes a suite that may use a preprocessor
    written in python.
    """

    def preprocessor_source(self) -> str:
        raise NotImplementedError()

    def file_structure(self,
                       root_path: pathlib.Path,
                       python_executable_file_name: str,
                       preprocessor_source_file_name: str) -> DirContents:
        raise NotImplementedError()

    def first_arguments(self,
                        root_path: pathlib.Path,
                        python_executable_file_name: str,
                        preprocessor_source_file_name: str) -> list:
        raise NotImplementedError()


class SetupWithoutPreprocessor(SetupBase):
    def file_structure(self, root_path: pathlib.Path) -> DirContents:
        raise NotImplementedError()

    def first_arguments(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()


def run_in_sub_process(put: unittest.TestCase,
                       arguments: list) -> SubProcessResult:
    return run_shellcheck_in_sub_process(put, arguments)


def run_internally(put: unittest.TestCase,
                   arguments: list) -> SubProcessResult:
    return execute_main_program(arguments)


def check(additional_arguments: list,
          setup: SetupWithoutPreprocessor,
          put: unittest.TestCase,
          runner):
    """
    :param runner: (unittest.TestCase, list) -> SubProcessResult
    """
    with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-') as tmp_dir:
        tmp_dir_path = resolved_path(tmp_dir)
        setup.file_structure(tmp_dir_path).write_to(tmp_dir_path)
        file_argument = str(setup.file_argument_based_at(tmp_dir_path))
        first_arguments = setup.first_arguments(tmp_dir_path)
        arguments = first_arguments + ARGUMENTS_FOR_TEST_INTERPRETER + additional_arguments + [file_argument]
        sub_process_result = runner(put, arguments)
        # print(sub_process_result.stderr)
        setup.check(put,
                    tmp_dir_path,
                    sub_process_result)


def check_with_pre_proc(additional_arguments: list,
                        setup: SetupWithPreprocessor,
                        put: unittest.TestCase,
                        runner):
    """
    :param runner: (unittest.TestCase, list) -> SubProcessResult
    """
    with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-preprocessor-') as pre_proc_dir:
        preprocessor_file_path = resolved_path(pre_proc_dir) / 'preprocessor.py'
        with preprocessor_file_path.open('w') as f:
            f.write(setup.preprocessor_source())
        with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-dir-contents-') as tmp_dir:
            tmp_dir_path = resolved_path(tmp_dir)
            file_structure = setup.file_structure(tmp_dir_path,
                                                  sys.executable,
                                                  str(preprocessor_file_path))
            file_structure.write_to(tmp_dir_path)
            file_argument = str(setup.file_argument_based_at(tmp_dir_path))
            first_arguments = setup.first_arguments(tmp_dir_path, sys.executable, str(preprocessor_file_path))
            arguments = first_arguments + ARGUMENTS_FOR_TEST_INTERPRETER + additional_arguments + [file_argument]
            sub_process_result = runner(put, arguments)
            setup.check(put,
                        tmp_dir_path,
                        sub_process_result)


class TestsForSetupWithoutPreprocessorInternally(unittest.TestCase):
    def _check(self,
               additional_arguments: list,
               setup: SetupWithoutPreprocessor):
        check(additional_arguments, setup, self,
              run_internally)


class TestsForSetupWithoutPreprocessorExternally(unittest.TestCase):
    def _check(self,
               additional_arguments: list,
               setup: SetupWithoutPreprocessor):
        check(additional_arguments, setup, self,
              run_in_sub_process)


class TestsForSetupWithPreprocessorInternally(unittest.TestCase):
    def _check(self,
               additional_arguments: list,
               setup: SetupWithPreprocessor):
        check_with_pre_proc(additional_arguments, setup, self,
                            run_internally)


class TestsForSetupWithPreprocessorExternally(unittest.TestCase):
    def _check(self,
               additional_arguments: list,
               setup: SetupWithPreprocessor):
        check_with_pre_proc(additional_arguments, setup, self,
                            run_in_sub_process)
