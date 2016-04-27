import unittest

import exactly_lib_test
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTest(exactly_lib_test.suite())
    suite.addTest(exactly_lib_test.default.program_modes.suite_for(main_program_runner))
    return suite


def run_suite_for(main_program_runner: MainProgramRunner):
    suite = suite_for(main_program_runner)
    runner = unittest.TextTestRunner()
    runner.run(suite)
