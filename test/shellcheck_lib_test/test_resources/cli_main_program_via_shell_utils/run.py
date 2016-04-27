import pathlib
import unittest

from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.process import run_subprocess, SubProcessResult

SRC_DIR_NAME = 'src'
MAIN_PROGRAM_FILE_NAME = 'main-program-executor-for-test.py'


def shellcheck_src_path(dir_of_this_file: pathlib.Path) -> pathlib.Path:
    return dir_of_this_file.parent / SRC_DIR_NAME / MAIN_PROGRAM_FILE_NAME


def run_shellcheck_in_sub_process(puc: unittest.TestCase,
                                  arguments: list,
                                  stdin_contents: str = '') -> SubProcessResult:
    cwd = pathlib.Path.cwd()
    py_exe.assert_interpreter_is_available(puc)
    shellcheck_path = shellcheck_src_path(cwd)
    cmd_and_args = py_exe.args_for_interpreting(shellcheck_path, arguments)
    return run_subprocess(cmd_and_args, stdin_contents)


def contents_of_file(path: pathlib.Path) -> str:
    with path.open() as f:
        return f.read()
