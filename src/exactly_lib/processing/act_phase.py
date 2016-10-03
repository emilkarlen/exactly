import types

from exactly_lib.execution.act_phase import ActSourceExecutor
from exactly_lib.section_document.parse import SectionElementParser


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActPhaseParser can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls,
                parser: SectionElementParser,
                script_builder_constructor,
                executor: ActSourceExecutor):
        """
        :param script_builder_constructor: () -> ScriptSourceBuilder
        """
        return tuple.__new__(cls, (parser,
                                   script_builder_constructor,
                                   executor))

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
