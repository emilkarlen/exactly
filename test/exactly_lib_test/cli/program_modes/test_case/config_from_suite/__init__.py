import unittest

from exactly_lib_test.cli.program_modes.test_case.config_from_suite import config_reading, \
    fail_due_to_invalid_command_line_options
from exactly_lib_test.cli.test_resources.internal_main_program_runner import RunViaMainProgramInternally
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return config_reading.suite()


def suite_that_does_require_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    return fail_due_to_invalid_command_line_options.suite_for(mpr)


def _suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_that_does_not_require_main_program_runner(),
        suite_that_does_require_main_program_runner(RunViaMainProgramInternally())
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(_suite())
