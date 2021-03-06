import unittest

from exactly_lib_test.cli_default.program_modes.test_suite import \
    invalid_command_line_options, invalid_suites, \
    integration_tests, default_actor, wildcard_file_references, instruction_that_runs_program
from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_with_any_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(invalid_command_line_options.suite_for(main_program_runner))
    ret_val.addTest(invalid_suites.suite_for(main_program_runner))
    ret_val.addTest(wildcard_file_references.suite_for(main_program_runner))
    ret_val.addTest(integration_tests.suite_for(main_program_runner))
    ret_val.addTest(default_actor.suite_for(main_program_runner))
    ret_val.addTest(instruction_that_runs_program.suite_for(main_program_runner))
    return ret_val


if __name__ == '__main__':
    suite = suite_with_any_main_program_runner(main_program_runner_with_default_setup__in_same_process())
    unittest.TextTestRunner().run(suite)
