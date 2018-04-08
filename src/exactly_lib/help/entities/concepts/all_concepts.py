from typing import List

from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.entities.concepts.objects import \
    action_to_check, actor, \
    environment_variable, preprocessor, sandbox, shell_syntax, \
    home_directory_structure, test_case_directory_structure, \
    suite_reporter, symbol, type_, configuration_parameter, current_working_directory


def all_concepts() -> List[ConceptDocumentation]:
    return [
        actor.ACTOR_CONCEPT,
        action_to_check.ACTOR_CONCEPT,
        shell_syntax.SHELL_SYNTAX_CONCEPT,
        test_case_directory_structure.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT,
        home_directory_structure.HOME_DIRECTORY_STRUCTURE_CONCEPT,
        sandbox.SANDBOX_CONCEPT,
        symbol.SYMBOL_CONCEPT,
        current_working_directory.CURRENT_WORKING_DIRECTORY_CONCEPT,
        configuration_parameter.CONFIGURATION_PARAMETER_CONCEPT,
        environment_variable.ENVIRONMENT_VARIABLE_CONCEPT,
        preprocessor.PREPROCESSOR_CONCEPT,
        suite_reporter.SUITE_REPORTER_CONCEPT,
        type_.TYPE_CONCEPT,
    ]
