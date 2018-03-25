from typing import Sequence

from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.value_type import DataValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileRefResolver(DataValueResolver):
    """
    Resolver who's resolved value is of type `ValueType.PATH` / :class:`FileRef`
    """

    @property
    def data_value_type(self) -> DataValueType:
        return DataValueType.PATH

    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return str(type(self))
