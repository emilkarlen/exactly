import unittest

from exactly_lib_test.default import instruction_name_and_argument_splitter as splitter
from exactly_lib_test.default import program_modes
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return splitter.suite()


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return program_modes.suite_that_does_require_main_program_runner(main_program_runner)


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = suite_that_does_not_require_main_program_runner()
    ret_val.addTests(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


if __name__ == '__main__':
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        run_via_main_program_internally_with_default_setup

    unittest.TextTestRunner().run(complete_suite_for(run_via_main_program_internally_with_default_setup()))
