from exactly_lib.help.cross_reference_id import ActorCrossReferenceId, TestCasePhaseCrossReference
from exactly_lib.help.entity_names import ACTOR_ENTITY_TYPE_NAME
from exactly_lib.help.utils.entity_documentation import EntityDocumentation, EntitiesHelp
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text


class ActorDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self, name: str):
        self._name = name

    def singular_name(self) -> str:
        return self._name

    def cross_reference_target(self) -> ActorCrossReferenceId:
        return ActorCrossReferenceId(self._name)

    def single_line_description(self) -> Text:
        return docs.text(self.single_line_description_str())

    def name_and_single_line_description(self) -> Text:
        return docs.text(self.name_and_single_line_description_str())

    def name_and_single_line_description_str(self) -> str:
        return self.singular_name() + ' - ' + self.single_line_description_str()

    def single_line_description_str(self) -> str:
        raise NotImplementedError()

    def act_phase_contents(self) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        raise NotImplementedError()

    def act_phase_contents_syntax(self) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        raise NotImplementedError()

    def see_also(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return self.__see_also_common() + self._see_also_specific()

    def __see_also_common(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
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
