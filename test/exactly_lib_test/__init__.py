import unittest

from exactly_lib_test import act_phase_setups
from exactly_lib_test import default
from exactly_lib_test import execution
from exactly_lib_test import help
from exactly_lib_test import instructions
from exactly_lib_test import processing
from exactly_lib_test import section_document
from exactly_lib_test import test_case
from exactly_lib_test import test_resources
from exactly_lib_test import test_suite
from exactly_lib_test import util
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.main_program.main_program_runners import RunViaOsInSubProcess


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = suite_that_does_not_require_main_program_runner()
    ret_val.addTests(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    from exactly_lib_test import cli
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources.suite())
    ret_val.addTest(util.suite())
    ret_val.addTest(section_document.suite())
    ret_val.addTest(test_case.suite())
    ret_val.addTest(execution.suite())
    ret_val.addTest(processing.suite())
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(instructions.suite())
    ret_val.addTest(act_phase_setups.suite())
    ret_val.addTest(help.suite())
    ret_val.addTest(default.suite_that_does_not_require_main_program_runner())
    ret_val.addTest(cli.suite_that_does_not_require_main_program_runner())
    return ret_val


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    from exactly_lib_test import cli
    ret_val = default.suite_that_does_require_main_program_runner(main_program_runner)
    ret_val.addTests(cli.suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


if __name__ == '__main__':
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        run_via_main_program_internally_with_default_setup

    unittest.TextTestRunner().run(complete_suite_for(run_via_main_program_internally_with_default_setup()))
