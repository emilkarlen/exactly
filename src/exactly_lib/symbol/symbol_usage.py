from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.symbol.resolver_structure import SymbolContainer, SymbolValueResolver
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.util.symbol_table import Entry


class SymbolUsage:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class SymbolReference(SymbolUsage):
    """
    A reference to a named element that is assumed to have been previously defined.
    """

    def __init__(self,
                 name: str,
                 restrictions: ReferenceRestrictions):
        super().__init__(name)
        self._restrictions = restrictions

    @property
    def restrictions(self) -> ReferenceRestrictions:
        return self._restrictions


class SymbolDefinition(SymbolUsage, ObjectWithSymbolReferences):
    """
    Defines a named element so that it can be used via references to it.
    """

    def __init__(self,
                 name: str,
                 container: SymbolContainer):
        super().__init__(name)
        self._container = container

    @property
    def resolver_container(self) -> SymbolContainer:
        return self._container

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._container.resolver.references

    @property
    def symbol_table_entry(self) -> Entry:
        return Entry(self.name, self.resolver_container)


class SymbolUsageVisitor:
    """
    Visitor of `SymbolUsage`
    """

    def visit(self, usage: SymbolUsage):
        """
        :return: Return value from _visit... method
        """
        if isinstance(usage, SymbolDefinition):
            return self._visit_definition(usage)
        if isinstance(usage, SymbolReference):
            return self._visit_reference(usage)
        raise TypeError('Unknown {}: {}'.format(SymbolValueResolver, str(usage)))

    def _visit_definition(self, usage: SymbolDefinition):
        raise NotImplementedError('abstract method')

    def _visit_reference(self, usage: SymbolReference):
        raise NotImplementedError('abstract method')
