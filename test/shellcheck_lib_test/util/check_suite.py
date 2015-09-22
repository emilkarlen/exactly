import pathlib
import sys
import tempfile
import unittest

from shellcheck_lib_test.cli.utils.execute_main_program import execute_main_program
from shellcheck_lib_test.util.cli_main_program_via_shell_utils.run import run_shellcheck_in_sub_process
from shellcheck_lib_test.util.file_structure import DirContents
from shellcheck_lib_test.util.with_tmp_file import lines_content, SubProcessResult


class SetupBase:
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def expected_exit_code(self) -> int:
        raise NotImplementedError()

    def expected_stdout_lines(self, root_path: pathlib.Path) -> list:
        raise NotImplementedError()

    def suite_begin(self, file_path: pathlib.Path) -> str:
        return 'SUITE ' + str(file_path) + ': BEGIN'

    def suite_end(self, file_path: pathlib.Path) -> str:
        return 'SUITE ' + str(file_path) + ': END'

    def case(self, file_path: pathlib.Path, status: str) -> str:
        return 'CASE  ' + str(file_path) + ': ' + status


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


class SetupWithoutPreprocessor(SetupBase):
    def file_structure(self, root_path: pathlib.Path) -> DirContents:
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
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure(tmp_dir_path).write_to(tmp_dir_path)
        file_argument = str(setup.root_suite_file_based_at(tmp_dir_path))
        arguments = ['suite'] + additional_arguments + [file_argument]
        sub_process_result = runner(put, arguments)
        # print(sub_process_result.stderr)
        put.assertEqual(setup.expected_exit_code(),
                        sub_process_result.exitcode,
                        'Exit Code')
        stdout_lines = setup.expected_stdout_lines(tmp_dir_path)
        if stdout_lines is not None:
            expected_output = lines_content(setup.expected_stdout_lines(tmp_dir_path))
            put.assertEqual(expected_output,
                            sub_process_result.stdout,
                            'Output on stdout')


def check_with_pre_proc(additional_arguments: list,
                        setup: SetupWithPreprocessor,
                        put: unittest.TestCase,
                        runner):
    """
    :param runner: (unittest.TestCase, list) -> SubProcessResult
    """
    with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-preprocessor-') as pre_proc_dir:
        preprocessor_file_path = pathlib.Path(pre_proc_dir) / 'preprocessor.py'
        with preprocessor_file_path.open('w') as f:
            f.write(setup.preprocessor_source())
        with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-dir-contents-') as tmp_dir:
            tmp_dir_path = pathlib.Path(tmp_dir)
            file_structure = setup.file_structure(tmp_dir_path,
                                                  sys.executable,
                                                  str(preprocessor_file_path))
            file_structure.write_to(tmp_dir_path)
            file_argument = str(setup.root_suite_file_based_at(tmp_dir_path))
            arguments = ['suite'] + additional_arguments + [file_argument]
            sub_process_result = runner(put, arguments)
            print(sub_process_result.stderr)
            put.assertEqual(setup.expected_exit_code(),
                            sub_process_result.exitcode,
                            'Exit Code')
            stdout_lines = setup.expected_stdout_lines(tmp_dir_path)
            if stdout_lines is not None:
                expected_output = lines_content(setup.expected_stdout_lines(tmp_dir_path))
                put.assertEqual(expected_output,
                                sub_process_result.stdout,
                                'Output on stdout')
