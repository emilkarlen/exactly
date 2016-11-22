import unittest

import exactly_lib_test
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return exactly_lib_test.complete_suite_for(main_program_runner)


def run_suite_for(main_program_runner: MainProgramRunner):
    suite = suite_for(main_program_runner)
    runner = unittest.TextTestRunner()
    runner.run(suite)
