import unittest

from exactly_lib_test.cli.program_modes.test_suite import argument_parsing, reporting_junit
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return argument_parsing.suite()


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return reporting_junit.suite_for(main_program_runner)


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = suite_that_does_not_require_main_program_runner()
    ret_val.addTests(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


def _run_complete_suite():
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    unittest.TextTestRunner().run(complete_suite_for(main_program_runner_with_default_setup__in_same_process()))


if __name__ == '__main__':
    _run_complete_suite()
