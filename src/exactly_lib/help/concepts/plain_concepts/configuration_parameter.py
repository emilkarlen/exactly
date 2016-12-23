from exactly_lib.help.concepts.configuration_parameters.all_configuration_parameters import all_configuration_parameters
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.concepts.utils import sorted_concepts_list
from exactly_lib.help.utils.name_and_cross_ref import Name
from exactly_lib.help.utils.phase_names import CONFIGURATION_PHASE_NAME
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.structures import text


class _ConfigurationParameterConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('configuration parameter', 'configuration parameters'))

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(text(_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION.format(CONFIGURATION_PHASE_NAME)),
                        [sorted_concepts_list(all_configuration_parameters())]))


CONFIGURATION_PARAMETER_CONCEPT = _ConfigurationParameterConcept()

_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION = """\
A value set by the {0} phase that determine how the remaining phases are executed."""
