from exactly_lib.help.concepts.plain_concepts.configuration_parameter import CONFIGURATION_PARAMETER_CONCEPT
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.concepts.plain_concepts.shell_syntax import SHELL_SYNTAX_CONCEPT
from exactly_lib.help.concepts.plain_concepts.suite_reporter import SUITE_REPORTER_CONCEPT
from exactly_lib.help.concepts.plain_concepts.symbol import SYMBOL_CONCEPT
from exactly_lib.help.concepts.plain_concepts.type_ import TYPE_CONCEPT


def all_plain_concepts() -> list:
    """
    :rtype [PlainConceptDocumentation]
    """
    return [
        SHELL_SYNTAX_CONCEPT,
        SANDBOX_CONCEPT,
        SYMBOL_CONCEPT,
        CONFIGURATION_PARAMETER_CONCEPT,
        ENVIRONMENT_VARIABLE_CONCEPT,
        PREPROCESSOR_CONCEPT,
        CURRENT_WORKING_DIRECTORY_CONCEPT,
        SUITE_REPORTER_CONCEPT,
        TYPE_CONCEPT,
    ]
