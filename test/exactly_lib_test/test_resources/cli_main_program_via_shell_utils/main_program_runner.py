import os
import sys
import unittest

from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult, run_subprocess


class RunInstalledProgramViaOsInSubProcess(MainProgramRunner):
    def __init__(self, executable_file_name_base: str):
        self._executable_file_name_base = executable_file_name_base
        self._main_program_path = _find_executable(executable_file_name_base)

    def description_for_test_name(self) -> str:
        return 'run installed program'

    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        if self._main_program_path is None:
            put.fail('Cannot find executable "%s" in path.' % self._executable_file_name_base)
        cmd_and_args = [self._main_program_path] + arguments
        stdin_contents = ''
        return run_subprocess(cmd_and_args, stdin_contents)


def _find_executable(executable, path=None):
    #
    # https://gist.github.com/4368898
    # Public domain code by anatoly techtonik <techtonik@gmail.com>
    #
    # NOTE: Some part of the function have been removed, since not used in this context.
    #
    """Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None
