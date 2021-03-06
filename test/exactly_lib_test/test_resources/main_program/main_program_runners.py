import unittest
from typing import List

from exactly_lib_test.test_resources.main_program.main_program_check_base import \
    run_default_main_program_via_sub_process
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.process import SubProcessResult


class RunDefaultMainProgramViaOsInSubProcess(MainProgramRunner):
    def description_for_test_name(self) -> str:
        return 'run via OS in sub-process'

    def run(self, put: unittest.TestCase, arguments: List[str]) -> SubProcessResult:
        return run_default_main_program_via_sub_process(put, arguments)
