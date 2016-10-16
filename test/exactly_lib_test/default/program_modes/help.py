import unittest

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND
from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.execution import phases
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.program_modes.test_case.config import phase_help_name
from exactly_lib.test_suite import parser as suite_parser
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_set import INSTRUCTION_NAME__ACTOR
from exactly_lib_test.test_resources import process_result_assertions as pr
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase, Arrangement
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import is_empty, is_not_only_space


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_suite_for_test_cases(main_program_test_cases(), main_program_runner))
    ret_val.addTest(test_suite_for_test_cases(main_program_test_cases_for_all_case_phases(), main_program_runner))
    ret_val.addTest(test_suite_for_test_cases(main_program_test_cases_for_all_suite_sections(), main_program_runner))
    return ret_val


def main_program_test_cases() -> list:
    return [
        ProcessTestCase('WHEN command line arguments are invalid THEN'
                        ' exit code SHOULD indicate this'
                        ' AND stdout SHOULD be empty',
                        HelpInvokation(['too', 'many', 'arguments', ',', 'indeed']),
                        va.And([
                            pr.is_result_for_exit_code(main_program.EXIT_INVALID_USAGE),
                            pr.stdout(is_empty())
                        ])),
        ProcessTestCase('help for "program" SHOULD be successful',
                        HelpInvokation(arguments_for.program()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "help" SHOULD be successful',
                        HelpInvokation(arguments_for.help_help()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case cli syntax" SHOULD be successful',
                        HelpInvokation(arguments_for.case_cli_syntax()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case specification" SHOULD be successful',
                        HelpInvokation(arguments_for.case_specification()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case instruction in phase" SHOULD be successful',
                        HelpInvokation(arguments_for.case_instruction_in_phase(phase_help_name(phases.SETUP),
                                                                               CHANGE_DIR_INSTRUCTION_NAME)),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case instructions" SHOULD be successful',
                        HelpInvokation(arguments_for.case_instructions()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "case instruction search" SHOULD be successful',
                        HelpInvokation(arguments_for.case_instruction_search(CHANGE_DIR_INSTRUCTION_NAME)),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "suite cli syntax" SHOULD be successful',
                        HelpInvokation(arguments_for.suite_cli_syntax()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "suite specification" SHOULD be successful',
                        HelpInvokation(arguments_for.suite_specification()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "suite section instruction" SHOULD be successful',
                        HelpInvokation(arguments_for.suite_instruction_in_section(suite_parser.SECTION_NAME__CONF,
                                                                                  INSTRUCTION_NAME__ACTOR)),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "concept list" SHOULD be successful',
                        HelpInvokation(arguments_for.concept_list()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "individual concept" SHOULD be successful',
                        HelpInvokation(arguments_for.concept_single(SANDBOX_CONCEPT.name().singular)),
                        _RESULT_IS_SUCCESSFUL),
    ]


def main_program_test_cases_for_all_suite_sections() -> list:
    return [
        ProcessTestCase("""help for "suite/section '%s'" SHOULD be successful""" % section_name,
                        HelpInvokation(arguments_for.suite_section_for_name(section_name)),
                        _RESULT_IS_SUCCESSFUL)
        for section_name in suite_parser.ALL_SECTION_NAMES
        ]


def main_program_test_cases_for_all_case_phases() -> list:
    return [
        ProcessTestCase("""help for "case/phase '%s'" SHOULD be successful""" % phase.section_name,
                        HelpInvokation(arguments_for.case_phase(phase)),
                        _RESULT_IS_SUCCESSFUL)
        for phase in phases.ALL
        ]


class HelpInvokation(Arrangement):
    def __init__(self,
                 help_arguments: list):
        self.help_arguments = help_arguments

    def command_line_arguments(self) -> list:
        return [HELP_COMMAND] + self.help_arguments


_RESULT_IS_SUCCESSFUL = va.And([pr.is_result_for_exit_code(0), pr.stdout(is_not_only_space())])
