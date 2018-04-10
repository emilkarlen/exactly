from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import conf_params
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class _ActionToCheckConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.ACTION_TO_CHECK_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(concepts.ACTION_TO_CHECK_CONCEPT_INFO.single_line_description,
                                          docs.empty_section_contents())

    def see_also_targets(self) -> list:
        return (
            [
                TestCasePhaseCrossReference(phase_names.ACT_PHASE_NAME.plain),
                concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
            ]
        )


ACTOR_CONCEPT = _ActionToCheckConcept()
