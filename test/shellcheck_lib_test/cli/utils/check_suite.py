import pathlib
import tempfile
import unittest

from shellcheck_lib_test.cli.utils.execute_main_program import execute_main_program
from shellcheck_lib_test.util.file_structure import DirContents
from shellcheck_lib_test.util.with_tmp_file import lines_content


class Setup:
    def root_suite_file_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure(self, root_path: pathlib.Path) -> DirContents:
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
        return str(file_path) + ': ' + status


def check(additional_arguments: list,
          setup: Setup,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure(tmp_dir_path).write_to(tmp_dir_path)
        arguments = ['suite'] + additional_arguments + [str(setup.root_suite_file_based_at(tmp_dir_path))]
        exit_code, stdout_contents, stderr_contents = execute_main_program(arguments)
        put.assertEqual(setup.expected_exit_code(),
                        exit_code,
                        'Exit Code')
        expected_output = lines_content(setup.expected_stdout_lines(tmp_dir_path))
        put.assertEqual(expected_output,
                        stdout_contents,
                        'Output on stdout')
