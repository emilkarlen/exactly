import unittest

from exactly_lib_test.cli import program_modes
from exactly_lib_test.cli.util import value_lookup
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_lookup.suite(),
        program_modes.suite_that_does_not_require_main_program_runner(),
    ])


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return program_modes.suite_that_does_require_main_program_runner(main_program_runner)


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = suite_that_does_not_require_main_program_runner()
    ret_val.addTests(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


if __name__ == '__main__':
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    unittest.TextTestRunner().run(complete_suite_for(main_program_runner_with_default_setup__in_same_process()))
