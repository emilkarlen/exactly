import unittest

from exactly_lib_test.cli.program_modes.help import z_package_suite as help
from exactly_lib_test.cli.program_modes.symbol import z_package_suite as symbol
from exactly_lib_test.cli.program_modes.test_case import z_package_suite as test_case
from exactly_lib_test.cli.program_modes.test_suite import z_package_suite as test_suite
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_case.suite_that_does_not_require_main_program_runner(),
        test_suite.suite_that_does_not_require_main_program_runner(),
        symbol.suite(),
        help.suite(),
    ])


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return unittest.TestSuite([
        test_case.suite_that_does_require_main_program_runner(main_program_runner),
        test_suite.suite_that_does_require_main_program_runner(main_program_runner),
    ])


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_that_does_not_require_main_program_runner(),
        suite_that_does_require_main_program_runner(main_program_runner),
    ])


def _run_complete_suite():
    from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    unittest.TextTestRunner().run(complete_suite_for(main_program_runner_with_default_setup__in_same_process()))


if __name__ == '__main__':
    _run_complete_suite()
