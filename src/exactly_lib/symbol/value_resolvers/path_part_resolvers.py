from exactly_lib.symbol.concrete_restrictions import StringRestriction
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.symbol.value_resolvers.path_part_resolver import PathPartResolver
from exactly_lib.symbol.value_structure import SymbolReference, ValueContainer
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable


class PathPartResolverAsFixedPath(PathPartResolver):
    def __init__(self, file_name: str):
        self._path_part = PathPartAsFixedPath(file_name)

    def resolve(self, symbols: SymbolTable) -> PathPart:
        return self._path_part

    @property
    def references(self) -> list:
        return []


class PathPartResolverAsNothing(PathPartResolver):
    def resolve(self, symbols: SymbolTable) -> PathPart:
        return PathPartAsNothing()

    @property
    def references(self) -> list:
        return []


class PathPartResolverAsStringSymbolReference(PathPartResolver):
    def __init__(self, symbol_name: str):
        self._symbol_reference = SymbolReference(symbol_name, StringRestriction())

    def resolve(self, symbols: SymbolTable) -> PathPart:
        value_container = symbols.lookup(self._symbol_name)
        assert isinstance(value_container, ValueContainer)
        string_value = value_container.value
        assert isinstance(string_value, StringResolver)
        path_string = string_value.resolve(symbols)
        return PathPartAsFixedPath(path_string)

    @property
    def references(self) -> list:
        return [self._symbol_reference]

    @property
    def _symbol_name(self) -> str:
        return self._symbol_reference.name

    def __str__(self):
        return '{}({})'.format(type(self), repr(self._symbol_name))
