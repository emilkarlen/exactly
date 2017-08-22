from exactly_lib.named_element.resolver_structure import SymbolValueResolver
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileRefResolver(SymbolValueResolver):
    """
    Resolver who's resolved value is of type `ValueType.PATH` / :class:`FileRef`
    """

    @property
    def value_type(self) -> ValueType:
        return ValueType.PATH

    def resolve(self, symbols: SymbolTable) -> FileRef:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        raise NotImplementedError()

    def __str__(self):
        return str(type(self))
