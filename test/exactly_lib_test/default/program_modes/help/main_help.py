import unittest

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND
from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.help.actors.names_and_cross_references import SINGLE_COMMAND_LINE_ACTOR__NAME
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase, Arrangement
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import is_empty, is_not_only_space


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite_for_test_cases(_main_program_test_cases(), main_program_runner)


def _main_program_test_cases() -> list:
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

        ProcessTestCase('help for "concept list" SHOULD be successful',
                        HelpInvokation(arguments_for.concept_list()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "individual concept" SHOULD be successful',
                        HelpInvokation(arguments_for.concept_single(SANDBOX_CONCEPT.name().singular)),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "actor list" SHOULD be successful',
                        HelpInvokation(arguments_for.actor_list()),
                        _RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "actor concept" SHOULD be successful',
                        HelpInvokation(arguments_for.actor_single(SINGLE_COMMAND_LINE_ACTOR__NAME)),
                        _RESULT_IS_SUCCESSFUL),
    ]


class HelpInvokation(Arrangement):
    def __init__(self,
                 help_arguments: list):
        self.help_arguments = help_arguments

    def command_line_arguments(self) -> list:
        return [HELP_COMMAND] + self.help_arguments


_RESULT_IS_SUCCESSFUL = va.And([pr.is_result_for_exit_code(0), pr.stdout(is_not_only_space())])
