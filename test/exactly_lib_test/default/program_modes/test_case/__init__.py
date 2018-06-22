import unittest

from exactly_lib_test.default.program_modes.test_case import misc, \
    command_line_options, output_result_of_act_phase, \
    preprocessing, \
    act_phase, \
    predefined_symbols
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_require_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(command_line_options.suite_for(mpr))
    ret_val.addTest(misc.suite_for(mpr))
    ret_val.addTest(preprocessing.suite_for(mpr))
    ret_val.addTest(act_phase.suite_for(mpr))
    return ret_val


def suite_that_does_require_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    return unittest.TestSuite([
        predefined_symbols.suite_that_requires_main_program_runner_with_default_setup(mpr),
        output_result_of_act_phase.suite_that_requires_main_program_runner_with_default_setup(mpr),
    ])


def _suite_with_main_program_runner_with_default_setup() -> unittest.TestSuite:
    mpr = main_program_runner_with_default_setup__in_same_process()
    ret_val = unittest.TestSuite()
    ret_val.addTest(suite_that_does_require_main_program_runner(mpr))
    ret_val.addTest(suite_that_does_require_main_program_runner_with_default_setup(mpr))
    return ret_val


if __name__ == '__main__':
    suite = _suite_with_main_program_runner_with_default_setup()

    unittest.TextTestRunner().run(suite)
