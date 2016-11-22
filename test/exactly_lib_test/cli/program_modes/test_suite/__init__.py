import unittest

from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from . import reporting_junit


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return reporting_junit.suite_for(main_program_runner)
