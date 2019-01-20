from exactly_lib.test_case.actor import Actor


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the Actor can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls, actor: Actor):
        return tuple.__new__(cls, (actor,))

    @property
    def actor(self) -> Actor:
        return self[0]
