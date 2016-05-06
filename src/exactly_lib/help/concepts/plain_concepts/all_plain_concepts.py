from exactly_lib.help.concepts.plain_concepts.actor import ACTOR_CONCEPT
from exactly_lib.help.concepts.plain_concepts.configuration_parameter import CONFIGURATION_PARAMETER_CONCEPT
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT


def all_plain_concepts() -> list:
    """
    :rtype [PlainConceptDocumentation]
    """
    return [
        SANDBOX_CONCEPT,
        CONFIGURATION_PARAMETER_CONCEPT,
        ENVIRONMENT_VARIABLE_CONCEPT,
        PREPROCESSOR_CONCEPT,
        ACTOR_CONCEPT,
    ]
