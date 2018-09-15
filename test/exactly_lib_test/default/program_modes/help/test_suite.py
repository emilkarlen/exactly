import unittest
from typing import List

from exactly_lib.cli.definitions.program_modes.help import arguments_for
from exactly_lib.definitions.test_suite import section_names_plain
from exactly_lib.definitions.test_suite.instruction_names import INSTRUCTION_NAME__PREPROCESSOR
from exactly_lib_test.default.program_modes.help.test_resources import HelpInvokation, RESULT_IS_SUCCESSFUL
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_suite_for_test_cases(_global_test_cases(), main_program_runner)),
    ret_val.addTest(test_suite_for_test_cases(_test_cases_for_all_suite_sections(), main_program_runner))
    return ret_val


def _test_cases_for_all_suite_sections() -> List[ProcessTestCase]:
    return [
        ProcessTestCase("""help for "suite/section '%s'" SHOULD be successful""" % section_name,
                        HelpInvokation(arguments_for.suite_section_for_name(section_name)),
                        RESULT_IS_SUCCESSFUL)
        for section_name in section_names_plain.ALL_SUITE_SPECIFIC_SECTION_NAMES
        ]


def _global_test_cases() -> List[ProcessTestCase]:
    return [
        ProcessTestCase('help for "suite cli syntax" SHOULD be successful',
                        HelpInvokation(arguments_for.suite_cli_syntax()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "suite specification" SHOULD be successful',
                        HelpInvokation(arguments_for.suite_specification()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "suite section instruction" SHOULD be successful',
                        HelpInvokation(arguments_for.suite_instruction_in_section(
                            section_names_plain.SECTION_NAME__CONF,
                            INSTRUCTION_NAME__PREPROCESSOR)),
                        RESULT_IS_SUCCESSFUL),
    ]
