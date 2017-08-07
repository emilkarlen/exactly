import unittest

import exactly_lib_test
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def complete_without_main_program_runner() -> unittest.TestSuite:
    return exactly_lib_test.complete_without_main_program_runner()


def complete_with_any_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    return exactly_lib_test.complete_with_any_main_program_runner(mpr)


def complete_with_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    return exactly_lib_test.complete_with_main_program_runner_with_default_setup(mpr)
