from typing import List, Iterable

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.all_entity_types import ACTOR_ENTITY_TYPE_NAMES
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents


class ActorDocumentation(EntityDocumentation):
    """
    Documents an actor.
    """

    def main_description_rest(self) -> List[ParagraphItem]:
        return []

    def act_phase_contents(self) -> SectionContents:
        raise NotImplementedError()

    def act_phase_contents_syntax(self) -> SectionContents:
        raise NotImplementedError()

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list, which may contain duplicate elements.
        """
        return self.__see_also_common() + self._see_also_specific()

    @staticmethod
    def __see_also_common() -> List[SeeAlsoTarget]:
        return [
            concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
            phase_infos.ACT.cross_reference_target,
            phase_infos.CONFIGURATION.instruction_cross_reference_target(instruction_names.ACTOR_INSTRUCTION_NAME),
        ]

    def _see_also_specific(self) -> List[SeeAlsoTarget]:
        return []


def actors_help(actors: Iterable[ActorDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(ACTOR_ENTITY_TYPE_NAMES,
                          actors)
