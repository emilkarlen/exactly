from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES
from exactly_lib.help_texts.test_case import phase_names
from exactly_lib.util.textformat.structure.document import SectionContents


class ActorDocumentation(EntityDocumentation):
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

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return self.__see_also_common() + self._see_also_specific()

    def __see_also_common(self) -> list:
        """
        :rtype [`SeeAlsoTarget`]
        """
        return [
            concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseCrossReference(phase_names.ACT_PHASE_NAME.plain),
        ]

    def _see_also_specific(self) -> list:
        """
        :rtype [`SeeAlsoTarget`]
        """
        return []


def actors_help(actors: iter) -> EntityTypeHelp:
    """
    :param actors: [ActorDocumentation]
    """
    return EntityTypeHelp(ACTOR_ENTITY_TYPE_NAMES,
                          actors)
