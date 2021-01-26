from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.util.name_and_value import NameAndValue


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the NameAndValue[Actor] can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls, actor_name: str, actor: Actor):
        return tuple.__new__(cls, (actor_name, actor,))

    @staticmethod
    def of_nav(nav: NameAndValue[Actor]) -> 'ActPhaseSetup':
        return ActPhaseSetup(nav.name, nav.value)

    @property
    def actor_nav(self) -> NameAndValue[Actor]:
        return NameAndValue(self[0], self[1])
