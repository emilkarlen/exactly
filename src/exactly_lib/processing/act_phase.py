import types

from exactly_lib.execution.act_phase import ActSourceExecutor, ActSourceAndExecutorConstructor
from exactly_lib.section_document.parse import SectionElementParser


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActPhaseParser can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls,
                parser: SectionElementParser,  # TODO remove since replaced by source_and_executor_constructor
                script_builder_constructor,  # TODO remove since replaced by source_and_executor_constructor
                executor: ActSourceExecutor,  # TODO remove since replaced by source_and_executor_constructor
                source_and_executor_constructor: ActSourceAndExecutorConstructor):
        """
        :param script_builder_constructor: () -> ScriptSourceBuilder
        """
        return tuple.__new__(cls, (parser,
                                   script_builder_constructor,
                                   executor,
                                   source_and_executor_constructor))

    @property
    def parser(self) -> SectionElementParser:
        return self[0]

    @property
    def script_builder_constructor(self) -> types.FunctionType:
        """
        :return: () -> ScriptSourceBuilder
        """
        return self[1]

    @property
    def executor(self) -> ActSourceExecutor:
        return self[2]

    @property
    def source_and_executor_constructor(self) -> ActSourceAndExecutorConstructor:
        return self[3]
