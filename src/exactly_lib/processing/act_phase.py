from exactly_lib.execution.act_phase import ActSourceAndExecutorConstructor


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActPhaseParser can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls,
                source_and_executor_constructor: ActSourceAndExecutorConstructor):
        """
        :param script_builder_constructor: () -> ScriptSourceBuilder
        """
        return tuple.__new__(cls, (source_and_executor_constructor,))

    @property
    def source_and_executor_constructor(self) -> ActSourceAndExecutorConstructor:
        return self[0]
