import unittest

from exactly_lib.cli.cli_environment import exit_codes
from exactly_lib.cli.cli_environment.program_modes.help import arguments_for
from exactly_lib.default.program_modes.test_case import builtin_symbols
from exactly_lib.help.entities.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help_texts.entity import types, actors, syntax_element
from exactly_lib_test.default.program_modes.help.test_resources import HelpInvokation, RESULT_IS_SUCCESSFUL
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import is_empty


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite_for_test_cases(_main_program_test_cases(), main_program_runner)


def _main_program_test_cases() -> list:
    return [
        ProcessTestCase('WHEN command line arguments are invalid THEN'
                        ' exit code SHOULD indicate this'
                        ' AND stdout SHOULD be empty',
                        HelpInvokation(['too', 'many', 'arguments', ',', 'indeed']),
                        asrt.And([
                            pr.is_result_for_exit_code(exit_codes.EXIT_INVALID_USAGE),
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
                        HelpInvokation(arguments_for.actor_single(actors.COMMAND_LINE_ACTOR.singular_name)),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "type list" SHOULD be successful',
                        HelpInvokation(arguments_for.symbol_type()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for single "type" SHOULD be successful',
                        HelpInvokation(arguments_for.symbol_type(types.LINE_MATCHER_TYPE_INFO.name.singular)),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "builtin list" SHOULD be successful',
                        HelpInvokation(arguments_for.builtin()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for single "builtin" SHOULD be successful',
                        HelpInvokation(arguments_for.builtin(builtin_symbols.ALL[0].name)),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for "syntax list" SHOULD be successful',
                        HelpInvokation(arguments_for.syntax_element()),
                        RESULT_IS_SUCCESSFUL),

        ProcessTestCase('help for single "syntax" SHOULD be successful',
                        HelpInvokation(
                            arguments_for.syntax_element(syntax_element.ALL_SYNTAX_ELEMENTS[0].singular_name)),
                        RESULT_IS_SUCCESSFUL),
    ]
