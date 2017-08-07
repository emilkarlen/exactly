import shutil
import unittest

from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult, run_subprocess


class RunInstalledProgramViaOsInSubProcess(MainProgramRunner):
    def __init__(self, executable_file_name_base: str):
        self._executable_file_name_base = executable_file_name_base
        self._main_program_path = shutil.which(executable_file_name_base)

    def description_for_test_name(self) -> str:
        return 'run installed program'

    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        if self._main_program_path is None:
            put.fail('Cannot find executable "%s" in path.' % self._executable_file_name_base)
        cmd_and_args = [self._main_program_path] + arguments
        stdin_contents = ''
        return run_subprocess(cmd_and_args, stdin_contents)
