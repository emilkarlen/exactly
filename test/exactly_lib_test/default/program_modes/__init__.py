import unittest

from exactly_lib_test.default.program_modes import test_case, test_suite, help
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(help.suite_that_does_not_require_main_program_runner())
    ret_val.addTest(test_case.suite_that_does_not_require_main_program_runner())
    return ret_val


def suite_that_does_require_any_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite_that_does_require_main_program_runner(mpr))
    ret_val.addTest(test_suite.suite_with_any_main_program_runner(mpr))
    ret_val.addTest(help.suite_that_does_require_main_program_runner(mpr))
    return ret_val


def suite_that_does_require_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite_that_does_require_main_program_runner_with_default_setup(mpr))
    return ret_val


def _complete_with_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests(suite_that_does_not_require_main_program_runner())
    ret_val.addTests(suite_that_does_require_any_main_program_runner(mpr))
    return ret_val


if __name__ == '__main__':
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    unittest.TextTestRunner().run(
        _complete_with_main_program_runner_with_default_setup(main_program_runner_with_default_setup__in_same_process())
    )
