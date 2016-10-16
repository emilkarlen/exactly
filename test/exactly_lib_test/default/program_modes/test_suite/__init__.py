import unittest

from exactly_lib_test.default.program_modes.test_suite import integration_tests, reporting, default_actor
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(reporting.suite())
    ret_val.addTest(integration_tests.suite_for(main_program_runner))
    ret_val.addTest(default_actor.suite_for(main_program_runner))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
