from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable


class SymbolValueResolver:
    """
    Base class for values in the symbol table used by Exactly.
    """

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError()

    @property
    def references(self) -> list:
        """
        All :class:`SymbolReference` directly referenced by this object.

        :type: [`SymbolReference`]
        """
        raise NotImplementedError()

    def resolve(self, symbols: SymbolTable) -> DirDependentValue:
        """
        Resolves the value given a symbol table.
        :rtype: Depends on the concrete value.
        """
        raise NotImplementedError()

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds):
        """
        Short cut for resolving the value_of_any_dependency
        """
        return self.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)


class ResolverContainer(SymbolTableValue):
    """
    The info about a resolver that is stored in a symbol table.

    A value together with meta info
    """

    def __init__(self, value_resolver: SymbolValueResolver, source: Line):
        self._source = source
        self._resolver = value_resolver
        self._source = source

    @property
    def definition_source(self) -> Line:
        """The source code of the definition of the value."""
        return self._source

    @property
    def resolver(self) -> SymbolValueResolver:
        return self._resolver
