import unittest

from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from . import argument_parsing, config_from_suite, keep_sandbox


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return unittest.TestSuite([
        argument_parsing.suite(),
        keep_sandbox.suite(),
        config_from_suite.suite_that_does_not_require_main_program_runner(),
    ])


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return config_from_suite.suite_that_does_require_main_program_runner(main_program_runner)
