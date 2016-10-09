import types

from exactly_lib.execution.act_phase import ActSourceExecutor, ActSourceAndExecutorConstructor
from exactly_lib.section_document.parse import SectionElementParser


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
    def parser(self) -> SectionElementParser:
        raise ValueError('Should not be used anymore: ' + str(ActPhaseSetup))

    @property
    def script_builder_constructor(self) -> types.FunctionType:
        """
        :return: () -> ScriptSourceBuilder
        """
        raise ValueError('Should not be used anymore: ' + str(ActPhaseSetup))

    @property
    def executor(self) -> ActSourceExecutor:
        raise ValueError('Should not be used anymore: ' + str(ActPhaseSetup))

    @property
    def source_and_executor_constructor(self) -> ActSourceAndExecutorConstructor:
        return self[0]
