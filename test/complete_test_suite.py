import unittest

import shellcheck_lib_test
from shellcheck_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTest(shellcheck_lib_test.suite())
    suite.addTest(shellcheck_lib_test.default.program_modes.test_case.suite_for(main_program_runner))
    suite.addTest(shellcheck_lib_test.default.program_modes.test_suite.suite_for(main_program_runner))
    suite.addTest(shellcheck_lib_test.default.program_modes.html_doc.suite_for_main_program(main_program_runner))
    return suite


def run_suite_for(main_program_runner: MainProgramRunner):
    suite = suite_for(main_program_runner)
    runner = unittest.TextTestRunner()
    runner.run(suite)
