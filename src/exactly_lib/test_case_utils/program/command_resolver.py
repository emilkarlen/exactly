from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.process_execution.os_process_execution import Command


class CommandResolver(ObjectWithTypedSymbolReferences):
    """
    Resolves the command string to execute.
    """

    def __init__(self, arguments: ListResolver):
        self._arguments = arguments

    @property
    def arguments(self) -> ListResolver:
        return self._arguments

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        raise NotImplementedError('abstract method')
