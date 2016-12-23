from exactly_lib.help.concepts.configuration_parameters.all_configuration_parameters import all_configuration_parameters
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.concepts.names_and_cross_references import CONFIGURATION_PARAMETER_CONCEPT_INFO
from exactly_lib.help.concepts.utils import sorted_concepts_list
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description


class _ConfigurationParameterConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(CONFIGURATION_PARAMETER_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(self.single_line_description(),
                        [sorted_concepts_list(all_configuration_parameters())]))


CONFIGURATION_PARAMETER_CONCEPT = _ConfigurationParameterConcept()
