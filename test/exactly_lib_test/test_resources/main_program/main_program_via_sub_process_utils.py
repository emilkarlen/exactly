import pathlib
import unittest
from typing import List

from exactly_lib_test.test_resources.process import SubProcessResult, run_subprocess
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe

SRC_DIR_NAME = 'src'
MAIN_PROGRAM_FILE_NAME = 'default-main-program-runner.py'


def main_program_src_path(dir_of_this_file: pathlib.Path) -> pathlib.Path:
    prj_dir = dir_of_this_file.parent.parent.parent.parent
    return prj_dir / SRC_DIR_NAME / MAIN_PROGRAM_FILE_NAME


def run_default_main_program_via_sub_process(put: unittest.TestCase,
                                             arguments: List[str],
                                             stdin_contents: str = '') -> SubProcessResult:
    dir_of_this_file = pathlib.Path(__file__).parent
    py_exe.assert_interpreter_is_available(put)
    main_program_path = main_program_src_path(dir_of_this_file)
    cmd_and_args = py_exe.args_for_interpreting(main_program_path, arguments)
    return run_subprocess(cmd_and_args, stdin_contents)


def contents_of_file(path: pathlib.Path) -> str:
    with path.open() as f:
        return f.read()
