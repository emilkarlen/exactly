import unittest
from typing import List

from exactly_lib.cli.definitions.program_modes.help import arguments_for
from exactly_lib.definitions.cross_ref.concrete_cross_refs import HelpPredefinedContentsPart
from exactly_lib_test.cli_default.program_modes.help.test_resources import HelpInvokation, RESULT_IS_SUCCESSFUL
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_suite_for_test_cases(_parts_test_cases(), main_program_runner)),
    return ret_val


def _parts_test_cases() -> List[ProcessTestCase]:
    return [
        ProcessTestCase('help for part "{}" SHOULD be successful'.format(part),
                        HelpInvokation(arguments_for.ARGUMENTS_FOR_PART[part]()),
                        RESULT_IS_SUCCESSFUL)
        for part in HelpPredefinedContentsPart
    ]
