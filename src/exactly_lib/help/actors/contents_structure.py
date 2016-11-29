from exactly_lib.help.cross_reference_id import ActorCrossReferenceId, TestCasePhaseCrossReference
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text


class ActorDocumentation:
    """
    Abstract base class for concepts.
    """

    def __init__(self, name: str):
        self._name = name

    def name(self) -> str:
        return self._name

    def cross_reference_target(self) -> ActorCrossReferenceId:
        return ActorCrossReferenceId(self._name)

    def single_line_description(self) -> Text:
        return docs.text(self.single_line_description_str())

    def name_and_single_line_description(self) -> Text:
        return docs.text(self.name_and_single_line_description_str())

    def name_and_single_line_description_str(self) -> str:
        return self.name() + ' - ' + self.single_line_description_str()

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
        return self._see_also_common() + self._see_also_specific()

    def _see_also_common(self) -> list:
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


class ActorsHelp(tuple):
    def __new__(cls,
                actors: iter):
        """
        :type concepts: [`ActorDocumentation`]
        """
        return tuple.__new__(cls, (list(actors),))

    @property
    def all_actors(self) -> list:
        """
        :type: [`ActorDocumentation`]
        """
        return self[0]

    def lookup_by_name_in_singular(self, actor_name: str) -> ActorDocumentation:
        matches = list(filter(lambda c: c.name() == actor_name, self.all_actors))
        if not matches:
            raise KeyError('Not an actor: ' + actor_name)
        return matches[0]
