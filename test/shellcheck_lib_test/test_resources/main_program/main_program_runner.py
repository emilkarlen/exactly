import unittest

from shellcheck_lib_test.test_resources.main_program.main_program_check_base import run_in_sub_process, run_internally
from shellcheck_lib_test.test_resources.process import SubProcessResult


class MainProgramRunner:
    def run(self, put: unittest.TestCase,
            arguments: list) -> SubProcessResult:
        raise NotImplementedError()

    def __call__(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return self.run(put, arguments)


class RunViaOsInSubProcess(MainProgramRunner):
    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return run_in_sub_process(put, arguments)


class RunViaMainProgramInternally(MainProgramRunner):
    def run(self, put: unittest.TestCase, arguments: list) -> SubProcessResult:
        return run_internally(put, arguments)
