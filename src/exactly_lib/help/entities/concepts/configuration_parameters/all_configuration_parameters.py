from exactly_lib.help.entities.concepts.configuration_parameters.actor import ACTOR_CONCEPT
from exactly_lib.help.entities.concepts.configuration_parameters.execution_mode import \
    EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.entities.concepts.configuration_parameters.home_act_directory import \
    HOME_ACT_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.entities.concepts.configuration_parameters.home_case_directory import \
    HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.entities.concepts.configuration_parameters.timeout import TIMEOUT_CONFIGURATION_PARAMETER


def all_configuration_parameters() -> list:
    """
    :rtype [ConfigurationParameterDocumentation]
    """
    return [
        EXECUTION_MODE_CONFIGURATION_PARAMETER,
        HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER,
        HOME_ACT_DIRECTORY_CONFIGURATION_PARAMETER,
        ACTOR_CONCEPT,
        TIMEOUT_CONFIGURATION_PARAMETER,
    ]
