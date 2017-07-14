from exactly_lib.symbol.resolver_structure import ResolverContainer, SymbolValueResolver
from exactly_lib.symbol.value_restriction import ReferenceRestrictions
from exactly_lib.util.symbol_table import Entry


class SymbolUsage:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class SymbolDefinition(SymbolUsage):
    """
    Defines a symbol so that it can be used via references to it.
    """

    def __init__(self,
                 name: str,
                 container: ResolverContainer):
        super().__init__(name)
        self._container = container

    @property
    def resolver_container(self) -> ResolverContainer:
        return self._container

    @property
    def references(self) -> list:
        """All `SymbolReference` directly referenced by this object"""
        return self._container.resolver.references

    @property
    def symbol_table_entry(self) -> Entry:
        return Entry(self.name, self.resolver_container)


class SymbolReference(SymbolUsage):
    """
    A reference to a symbol that is assumed to have been previously defined.
    """

    def __init__(self,
                 name: str,
                 restrictions: ReferenceRestrictions):
        super().__init__(name)
        self._restrictions = restrictions

    @property
    def restrictions(self) -> ReferenceRestrictions:
        return self._restrictions


class SymbolUsageVisitor:
    """
    Visitor of `SymbolUsage`
    """

    def visit(self, symbol_usage: SymbolUsage):
        """
        :return: Return value from _visit... method
        """
        if isinstance(symbol_usage, SymbolDefinition):
            return self._visit_definition(symbol_usage)
        if isinstance(symbol_usage, SymbolReference):
            return self._visit_reference(symbol_usage)
        raise TypeError('Unknown {}: {}'.format(SymbolValueResolver, str(symbol_usage)))

    def _visit_definition(self, symbol_usage: SymbolDefinition):
        raise NotImplementedError()

    def _visit_reference(self, symbol_usage: SymbolReference):
        raise NotImplementedError()
