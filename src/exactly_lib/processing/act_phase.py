from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActPhaseParser can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls,
                source_and_executor_constructor: ActSourceAndExecutorConstructor):
        return tuple.__new__(cls, (source_and_executor_constructor,))

    @property
    def source_and_executor_constructor(self) -> ActSourceAndExecutorConstructor:
        return self[0]
