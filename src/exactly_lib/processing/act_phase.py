import types

from exactly_lib.execution.act_phase import ActSourceExecutor
from exactly_lib.execution.partial_execution import ActPhaseParser
from exactly_lib.section_document.parse import SectionElementParser


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActPhaseParser can completely replace this class
    (since the other members probably will be refactored away)
    """
    def __new__(cls,
                parser: SectionElementParser,
                script_builder_constructor,
                executor: ActSourceExecutor,
                phase_contents_parser: ActPhaseParser):
        """
        :param script_builder_constructor: () -> ScriptSourceBuilder
        """
        return tuple.__new__(cls, (parser,
                                   script_builder_constructor,
                                   executor,
                                   phase_contents_parser))

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
    def phase_contents_parser(self) -> ActPhaseParser:
        return self[3]
