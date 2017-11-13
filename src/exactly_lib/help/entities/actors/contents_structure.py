from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase, \
    command_line_names_as_singular_name
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseCrossReference
from exactly_lib.help_texts.entity.concepts import ACTOR_CONF_PARAM_INFO
from exactly_lib.util.textformat.structure.document import SectionContents

ACTOR_ENTITY_TYPE_NAMES = command_line_names_as_singular_name(ACTOR_CONF_PARAM_INFO.name)


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

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return self.__see_also_common() + self._see_also_specific()

    def __see_also_common(self) -> list:
        """
        :rtype [`SeeAlsoTarget`]
        """
        from exactly_lib.help.entities.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME
        return [
            ACTOR_CONCEPT.cross_reference_target(),
            TestCasePhaseCrossReference(ACT_PHASE_NAME.plain),
        ]

    def _see_also_specific(self) -> list:
        """
        :rtype [`SeeAlsoTarget`]
        """
        return []


def actors_help(actors: iter) -> EntitiesHelp:
    """
    :param actors: [ActorDocumentation]
    """
    return EntitiesHelp(ACTOR_ENTITY_TYPE_NAMES,
                        actors)
