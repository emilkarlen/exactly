from exactly_lib.definitions.entity import actors
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.conf_params import ACTOR_CONF_PARAM_INFO
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class _ActorConcept(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(ACTOR_CONF_PARAM_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(self.single_line_description(),
                                          docs.section_contents([]))

    def see_also_targets(self) -> list:
        return (
                [
                    concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                    phase_infos.CONFIGURATION.instruction_cross_reference_target(ACTOR_INSTRUCTION_NAME),
                ]
                +
                actors.all_actor_cross_refs()
        )


DOCUMENTATION = _ActorConcept()
