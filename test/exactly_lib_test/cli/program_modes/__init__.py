import unittest

from exactly_lib_test.cli.program_modes import help, test_case, test_suite
from exactly_lib_test.default import run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite())
    ret_val.addTest(help.suite())
    return ret_val


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite.suite_that_does_require_main_program_runner(main_program_runner)


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = suite_that_does_not_require_main_program_runner()
    ret_val.addTests(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(complete_suite_for(run_via_main_program_internally_with_default_setup()))
