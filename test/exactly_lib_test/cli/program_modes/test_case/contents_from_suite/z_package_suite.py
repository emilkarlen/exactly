import unittest

from exactly_lib_test.cli.program_modes.test_case.contents_from_suite import config_only_available_in_suite, \
    fail_due_to_invalid_command_line_options, propagation_of_case_instructions
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.main_program.main_program_runner_via_same_process import \
    RunViaMainProgramInternally


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return unittest.TestSuite([
        config_only_available_in_suite.suite(),
        propagation_of_case_instructions.suite(),
    ])


def suite_that_does_require_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    return fail_due_to_invalid_command_line_options.suite_for(mpr)


def _suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_that_does_not_require_main_program_runner(),
        suite_that_does_require_main_program_runner(RunViaMainProgramInternally())
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite())
