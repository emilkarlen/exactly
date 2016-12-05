import unittest

from exactly_lib.cli import main_program
from exactly_lib.cli.cli_environment.program_modes.help import arguments_for
from exactly_lib.help.actors.names_and_cross_references import SINGLE_COMMAND_LINE_ACTOR
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib_test.default.program_modes.help.test_resources import HelpInvokation, RESULT_IS_SUCCESSFUL
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import is_empty


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
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "help" SHOULD be successful',
                        HelpInvokation(arguments_for.help_help()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "concept list" SHOULD be successful',
                        HelpInvokation(arguments_for.concept_list()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "individual concept" SHOULD be successful',
                        HelpInvokation(arguments_for.concept_single(SANDBOX_CONCEPT.name().singular)),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "actor list" SHOULD be successful',
                        HelpInvokation(arguments_for.actor_list()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "actor concept" SHOULD be successful',
                        HelpInvokation(arguments_for.actor_single(SINGLE_COMMAND_LINE_ACTOR.singular_name)),
                        RESULT_IS_SUCCESSFUL),
    ]
