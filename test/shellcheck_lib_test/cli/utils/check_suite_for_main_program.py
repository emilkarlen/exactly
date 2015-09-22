import pathlib
import tempfile
import unittest

from shellcheck_lib_test.cli.utils.execute_main_program import execute_main_program
from shellcheck_lib_test.util.check_suite import SetupWithoutPreprocessor
from shellcheck_lib_test.util.with_tmp_file import lines_content


def check(additional_arguments: list,
          setup: SetupWithoutPreprocessor,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure(tmp_dir_path).write_to(tmp_dir_path)
        arguments = ['suite'] + additional_arguments + [str(setup.root_suite_file_based_at(tmp_dir_path))]
        sub_process_result = execute_main_program(arguments)
        put.assertEqual(setup.expected_exit_code(),
                        sub_process_result.exitcode,
                        'Exit Code')
        stdout_lines = setup.expected_stdout_lines(tmp_dir_path)
        if stdout_lines is not None:
            expected_output = lines_content(setup.expected_stdout_lines(tmp_dir_path))
            put.assertEqual(expected_output,
                            sub_process_result.stdout,
                            'Output on stdout')
