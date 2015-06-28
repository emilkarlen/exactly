import pathlib
import tempfile
import unittest

from shellcheck_lib_test.util.check_suite import Setup
from shellcheck_lib_test.util.cli_main_program_via_shell_utils.run import run_shellcheck_in_sub_process
from shellcheck_lib_test.util.with_tmp_file import lines_content


def check(additional_arguments: list,
          setup: Setup,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-suite-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure(tmp_dir_path).write_to(tmp_dir_path)
        file_argument = str(setup.root_suite_file_based_at(tmp_dir_path))
        arguments = ['suite'] + additional_arguments + [file_argument]
        sub_process_result = run_shellcheck_in_sub_process(put,
                                                           arguments)
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
