import unittest

from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.default.program_modes.help.test_resources import HelpInvokation, RESULT_IS_SUCCESSFUL
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_suite_for_test_cases(_global_test_cases(), main_program_runner)),
    ret_val.addTest(test_suite_for_test_cases(_test_cases_for_all_case_phases(), main_program_runner))
    return ret_val


def _test_cases_for_all_case_phases() -> list:
    return [
        ProcessTestCase("""help for "case/phase '%s'" SHOULD be successful""" % phase.section_name,
                        HelpInvokation(arguments_for.case_phase(phase)),
                        RESULT_IS_SUCCESSFUL)
        for phase in phase_identifier.ALL
        ]


def _global_test_cases() -> list:
    return [
        ProcessTestCase('help for "case cli syntax" SHOULD be successful',
                        HelpInvokation(arguments_for.case_cli_syntax()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case specification" SHOULD be successful',
                        HelpInvokation(arguments_for.case_specification()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case instruction in phase" SHOULD be successful',
                        HelpInvokation(arguments_for.case_instruction_in_phase(phase_help_name(phase_identifier.SETUP),
                                                                               CHANGE_DIR_INSTRUCTION_NAME)),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case instructions" SHOULD be successful',
                        HelpInvokation(arguments_for.case_instructions()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case instruction search" SHOULD be successful',
                        HelpInvokation(arguments_for.case_instruction_search(CHANGE_DIR_INSTRUCTION_NAME)),
                        RESULT_IS_SUCCESSFUL),
    ]
