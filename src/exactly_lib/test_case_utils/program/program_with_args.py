from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences, \
    references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference


class ProgramWithArgsResolver(ObjectWithSymbolReferences):
    def __init__(self,
                 program: StringResolver,
                 arguments: ListResolver):
        self._program = program
        self._arguments = arguments

    @property
    def program(self) -> StringResolver:
        return self._program

    @property
    def arguments(self) -> ListResolver:
        return self._arguments

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self._program,
                                                               self.arguments])
