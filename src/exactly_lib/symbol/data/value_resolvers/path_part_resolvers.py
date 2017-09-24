from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.data.value_resolvers.path_part_resolver import PathPartResolver
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath, PathPartAsNothing
from exactly_lib.type_system.data.path_part import PathPart
from exactly_lib.type_system.data.string_value import StringValue
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


class PathPartResolverAsStringResolver(PathPartResolver):
    """
    The referenced symbol must not have any dir-dependencies -
    i.e. not contain references (direct or indirect) to FileRefs
    that are not absolute.
    """

    def __init__(self, string_resolver: StringResolver):
        self._string_resolver = string_resolver

    def resolve(self, symbols: SymbolTable) -> PathPart:
        string_value = self._string_resolver.resolve(symbols)
        assert isinstance(string_value, StringValue)
        path_string = string_value.value_when_no_dir_dependencies()
        return PathPartAsFixedPath(path_string)

    @property
    def references(self) -> list:
        return self._string_resolver.references

    def __str__(self):
        return '{}({})'.format(type(self), repr(self._string_resolver))
