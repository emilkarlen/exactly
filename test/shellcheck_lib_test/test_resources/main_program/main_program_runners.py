import unittest

from shellcheck_lib_test.test_resources.main_program.main_program_check_base import run_in_sub_process
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from shellcheck_lib_test.test_resources.process import SubProcessResult


class RunViaOsInSubProcess(MainProgramRunner):
    def description_for_test_name(self) -> str:
        return 'run via OS in sub-process'

    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return run_in_sub_process(put, arguments)
