import itertools
import unittest

from exactly_lib.cli.cli_environment import exit_codes
from exactly_lib.cli.cli_environment.program_modes.help import arguments_for
from exactly_lib.default.program_modes.test_case import builtin_symbols
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity import types, actors, syntax_elements, suite_reporters, conf_params
from exactly_lib.help_texts.entity.all_entity_types import CONCEPT_ENTITY_TYPE_NAMES, ACTOR_ENTITY_TYPE_NAMES, \
    CONF_PARAM_ENTITY_TYPE_NAMES, SUITE_REPORTER_ENTITY_TYPE_NAMES, SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, \
    TYPE_ENTITY_TYPE_NAMES, BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.help_texts.name_and_cross_ref import EntityTypeNames
from exactly_lib_test.default.program_modes.help.test_resources import HelpInvokation, RESULT_IS_SUCCESSFUL
from exactly_lib_test.test_resources.main_program.constant_arguments_check import ProcessTestCase
from exactly_lib_test.test_resources.main_program.constant_arguments_check_execution import test_suite_for_test_cases
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion_str import is_empty


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return test_suite_for_test_cases(_main_program_test_cases(), main_program_runner)


_ENTITY_CASES = [
    (CONCEPT_ENTITY_TYPE_NAMES, concepts.SANDBOX_CONCEPT_INFO.singular_name),
    (CONF_PARAM_ENTITY_TYPE_NAMES, conf_params.EXECUTION_MODE_CONF_PARAM_INFO.singular_name),
    (ACTOR_ENTITY_TYPE_NAMES, actors.COMMAND_LINE_ACTOR.singular_name),
    (TYPE_ENTITY_TYPE_NAMES, types.LINE_MATCHER_TYPE_INFO.name.singular),
    (BUILTIN_SYMBOL_ENTITY_TYPE_NAMES, builtin_symbols.ALL[0].name),
    (SYNTAX_ELEMENT_ENTITY_TYPE_NAMES, syntax_elements.ALL_SYNTAX_ELEMENTS[0].singular_name),
    (SUITE_REPORTER_ENTITY_TYPE_NAMES, suite_reporters.PROGRESS_REPORTER.singular_name),
]


def _main_program_test_cases() -> list:
    return _non_entities_help() + _entities_help()


def _non_entities_help() -> list:
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
    ]


def _entities_help() -> list:
    return list(itertools.chain.from_iterable(
        map(lambda entity_info: _entity_help_cases(entity_info[0], entity_info[1]),
            _ENTITY_CASES)
    ))


def _entity_help_cases(entity_type_names: EntityTypeNames,
                       name_of_existing_entity: str) -> list:
    return [
        ProcessTestCase(
            'help for list of "{entity_type_name}" SHOULD be successful'.format(
                entity_type_name=entity_type_names.identifier
            ),
            HelpInvokation(arguments_for.entity_help(entity_type_names)),
            RESULT_IS_SUCCESSFUL),

        ProcessTestCase(
            'help for single "{entity_type_name}" ("{entity_name}") SHOULD be successful'.format(
                entity_type_name=entity_type_names.identifier,
                entity_name=name_of_existing_entity

            ),
            HelpInvokation(
                arguments_for.entity_help(entity_type_names,
                                          name_of_existing_entity)),
            RESULT_IS_SUCCESSFUL),
    ]
