from exactly_lib.test_case.actor import ActionToCheckExecutorParser


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActionToCheckExecutorParser can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls, actor: ActionToCheckExecutorParser):
        return tuple.__new__(cls, (actor,))

    @property
    def actor(self) -> ActionToCheckExecutorParser:
        return self[0]
