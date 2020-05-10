import itertools
from abc import ABC
from typing import Sequence, Optional, List

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.type_system.value_type import ValueType, TypeCategory
from exactly_lib.util.line_source import LineSequence
from exactly_lib.util.symbol_table import SymbolTableValue, SymbolTable, Entry


class ObjectWithSymbolReferences:
    @property
    def references(self) -> Sequence['SymbolReference']:
        """
        All references directly referenced by this object.
        """
        return []


class SymbolDependentValue(ObjectWithSymbolReferences):
    """A value that may depend on symbols in a :class:`SymbolTable`"""

    def resolve(self, symbols: SymbolTable):
        """
        Gives the value, by substituting symbol references with symbol values

        :param symbols: Contains all symbols reported by :func:`references`, with
        the types specified by the references' :class:`ReferenceRestrictions`.
        """
        raise NotImplementedError('abstract method')


class SymbolDependentTypeValue(SymbolDependentValue):
    """A :class:`SymbolDependentValue` that represents a value of a type in the type system"""

    @property
    def type_category(self) -> TypeCategory:
        raise NotImplementedError('abstract method')

    @property
    def value_type(self) -> ValueType:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence['SymbolReference']:
        """
        All :class:`SymbolReference` directly referenced by this object.

        :type: [`SymbolReference`]
        """
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('abstract method')


class SymbolContainer(SymbolTableValue):
    """
    The info about a Symbol Dependent Value that is stored in a symbol table.

    A value together with meta info
    """

    def __init__(self,
                 value_sdv: SymbolDependentTypeValue,
                 value_type: ValueType,
                 source_location: Optional[SourceLocationInfo]):
        self._sdv = value_sdv
        self._value_type = value_type
        self._source_location = source_location

    @property
    def source_location(self) -> Optional[SourceLocationInfo]:
        return self._source_location

    @property
    def definition_source(self) -> LineSequence:
        """
        The source code of the definition of the value.

        :rtype None iff the symbol is built in.
        """
        return None \
            if self._source_location is None else \
            self._source_location.source_location_path.location.source

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def sdv(self) -> SymbolDependentTypeValue:
        return self._sdv


def container_of_builtin(value_sdv: SymbolDependentTypeValue) -> SymbolContainer:
    return SymbolContainer(value_sdv, value_sdv.value_type, None)


class Failure(ABC):
    pass


class ReferenceRestrictions(ABC):
    """
    Restrictions on a referenced symbol
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[Failure]:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :return: None if satisfied, otherwise a failure description
        """
        pass


class SymbolUsage:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


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


class SymbolDefinition(SymbolUsage, ObjectWithSymbolReferences):
    """
    Defines a symbol so that it can be used via references to it.
    """

    def __init__(self,
                 name: str,
                 container: SymbolContainer):
        super().__init__(name)
        self._container = container

    @property
    def symbol_container(self) -> SymbolContainer:
        return self._container

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._container.sdv.references

    @property
    def symbol_table_entry(self) -> Entry:
        return Entry(self.name, self.symbol_container)


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
        raise TypeError('Unknown {}: {}'.format(SymbolUsage, str(usage)))

    def _visit_definition(self, usage: SymbolDefinition):
        raise NotImplementedError('abstract method')

    def _visit_reference(self, usage: SymbolReference):
        raise NotImplementedError('abstract method')


def references_from_objects_with_symbol_references(objects: Sequence[ObjectWithSymbolReferences]
                                                   ) -> List[SymbolReference]:
    """Concatenates the references from all objects"""
    return list(itertools.chain.from_iterable([x.references
                                               for x in objects])
                )


def get_references(stv: SymbolDependentTypeValue) -> Sequence[SymbolReference]:
    return stv.references


def get_references__sdv(sdv: SymbolDependentValue) -> Sequence[SymbolReference]:
    return sdv.references


def get_type_category(sdv: SymbolDependentTypeValue) -> TypeCategory:
    return sdv.type_category


def get_value_type(sdv: SymbolDependentTypeValue) -> ValueType:
    return sdv.value_type
