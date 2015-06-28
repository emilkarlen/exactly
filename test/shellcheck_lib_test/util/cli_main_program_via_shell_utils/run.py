import pathlib
import sys
import unittest

from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.util.with_tmp_file import ExpectedSubProcessResult, lines_content, SubProcessResultInfo, \
    run_subprocess, run_subprocess_with_file_arg__full, SubProcessResult

SRC_DIR_NAME = 'src'
MAIN_PROGRAM_FILE_NAME = 'shellcheck.py'


def shellcheck_src_path(dir_of_this_file: pathlib.Path) -> pathlib.Path:
    return dir_of_this_file.parent / SRC_DIR_NAME / MAIN_PROGRAM_FILE_NAME


SUCCESSFUL_RESULT = ExpectedSubProcessResult(exitcode=FullResultStatus.PASS.value,
                                             stdout=lines_content([FullResultStatus.PASS.name]),
                                             stderr='')


def run_shellcheck_in_sub_process_with_file_argument(puc: unittest.TestCase,
                                                     file_contents: str,
                                                     flags: list=()) -> SubProcessResultInfo:
    cwd = pathlib.Path.cwd()
    # print('# DEBUG: cwd: ' + str(cwd))
    if not sys.executable:
        puc.fail('Cannot execute test since the name of the Python 3 interpreter is not found in sys.executable.')
    shellcheck_path = shellcheck_src_path(cwd)
    args_without_file = [sys.executable, str(shellcheck_path)] + list(flags)
    return run_subprocess_with_file_arg__full(args_without_file, file_contents)


def run_shellcheck_in_sub_process(puc: unittest.TestCase,
                                  arguments: list,
                                  stdin_contents: str='') -> SubProcessResult:
    cwd = pathlib.Path.cwd()
    # print('# DEBUG: cwd: ' + str(cwd))
    if not sys.executable:
        puc.fail('Cannot execute test since the name of the Python 3 interpreter is not found in sys.executable.')
    shellcheck_path = shellcheck_src_path(cwd)
    cmd_and_args = [sys.executable, str(shellcheck_path)] + list(arguments)
    return run_subprocess(cmd_and_args, stdin_contents)


def contents_of_file(path: pathlib.Path) -> str:
    with path.open() as f:
        return f.read()
