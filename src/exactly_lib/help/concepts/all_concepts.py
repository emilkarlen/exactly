from exactly_lib.help.concepts.configuration_parameters.all_configuration_parameters import all_configuration_parameters
from exactly_lib.help.concepts.plain_concepts.all_plain_concepts import all_plain_concepts


def all_concepts() -> list:
    """
    :rtype [ConceptDocumentation]
    """
    return all_plain_concepts() + all_configuration_parameters()
