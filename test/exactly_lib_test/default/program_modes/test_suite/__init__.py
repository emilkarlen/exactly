import unittest

from exactly_lib_test.default.program_modes.test_suite import integration_tests, default_actor, wildcard_file_references
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup_in_same_process
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_with_any_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(wildcard_file_references.suite_for(main_program_runner))
    ret_val.addTest(integration_tests.suite_for(main_program_runner))
    ret_val.addTest(default_actor.suite_for(main_program_runner))
    return ret_val


if __name__ == '__main__':
    suite = suite_with_any_main_program_runner(main_program_runner_with_default_setup_in_same_process())
    unittest.TextTestRunner().run(suite)
