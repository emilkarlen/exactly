from exactly_lib.named_element.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.named_element.resolver_structure import NamedElementContainer, NamedElementResolver
from exactly_lib.named_element.restriction import ReferenceRestrictions
from exactly_lib.util.symbol_table import Entry


class NamedElementUsage:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class NamedElementDefinition(NamedElementUsage, ObjectWithSymbolReferences):
    """
    Defines a named element so that it can be used via references to it.
    """

    def __init__(self,
                 name: str,
                 container: NamedElementContainer):
        super().__init__(name)
        self._container = container

    @property
    def resolver_container(self) -> NamedElementContainer:
        return self._container

    @property
    def references(self) -> list:
        return self._container.resolver.references

    @property
    def symbol_table_entry(self) -> Entry:
        return Entry(self.name, self.resolver_container)


class NamedElementReference(NamedElementUsage):
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


class NamedElementUsageVisitor:
    """
    Visitor of `NamedElementUsage`
    """

    def visit(self, usage: NamedElementUsage):
        """
        :return: Return value from _visit... method
        """
        if isinstance(usage, NamedElementDefinition):
            return self._visit_definition(usage)
        if isinstance(usage, NamedElementReference):
            return self._visit_reference(usage)
        raise TypeError('Unknown {}: {}'.format(NamedElementResolver, str(usage)))

    def _visit_definition(self, usage: NamedElementDefinition):
        raise NotImplementedError('abstract method')

    def _visit_reference(self, usage: NamedElementReference):
        raise NotImplementedError('abstract method')
