from exactly_lib.help.concepts.concept import all_plain_concepts
from exactly_lib.help.concepts.configuration_parameters.configuration_parameter import all_configuration_parameters


def all_concepts() -> list:
    """
    :rtype [ConceptDocumentation]
    """
    return all_plain_concepts() + all_configuration_parameters()
