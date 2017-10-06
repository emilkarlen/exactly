from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem
from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseCrossReference
from exactly_lib.help_texts.entity_names import ACTOR_ENTITY_TYPE_NAME
from exactly_lib.util.textformat.structure.document import SectionContents


class ActorDocumentation(EntityDocumentationBase):
    """
    Documents an actor.
    """

    def main_description_rest(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        return []

    def act_phase_contents(self) -> SectionContents:
        raise NotImplementedError()

    def act_phase_contents_syntax(self) -> SectionContents:
        raise NotImplementedError()

    def see_also_items(self) -> list:
        """
        :rtype: [`SeeAlsoItem`]
        """
        return [CrossReferenceIdSeeAlsoItem(x) for x in self.see_also_targets()]

    def see_also_targets(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return self.__see_also_common() + self._see_also_specific()

    def __see_also_common(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        from exactly_lib.help.entities.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
        return [
            ACTOR_CONCEPT.cross_reference_target(),
            TestCasePhaseCrossReference(ACT_PHASE_NAME.plain),
        ]

    def _see_also_specific(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return []


def actors_help(actors: iter) -> EntitiesHelp:
    """
    :param actors: [ActorDocumentation]
    """
    return EntitiesHelp(ACTOR_ENTITY_TYPE_NAME, actors)
