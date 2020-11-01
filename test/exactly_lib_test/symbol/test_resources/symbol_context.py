from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Sequence

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolReference, SymbolContainer, \
    ReferenceRestrictions, SymbolDefinition, SymbolUsage
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util import line_source
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.section_document.test_resources import source_location
from exactly_lib_test.test_resources import argument_renderer as args
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

SDV_TYPE = TypeVar('SDV_TYPE', bound=SymbolDependentValue)

ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION = source_location.source_info_for_line_sequence(
    line_source.single_line_sequence(1, 'definition source'))


class SymbolValueContext(Generic[SDV_TYPE], ABC):
    def __init__(self,
                 sdv: SDV_TYPE,
                 definition_source: Optional[SourceLocationInfo],
                 ):
        self._sdv = sdv
        self._definition_source = definition_source

    @property
    @abstractmethod
    def value_type(self) -> ValueType:
        pass

    @property
    def sdv(self) -> SDV_TYPE:
        return self._sdv

    @abstractmethod
    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        pass

    @property
    def definition_source(self) -> Optional[SourceLocationInfo]:
        return self._definition_source

    @property
    def container(self) -> SymbolContainer:
        return SymbolContainer(self.sdv, self.value_type, self.definition_source)


class SymbolContext(Generic[SDV_TYPE], ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    @abstractmethod
    def value(self) -> SymbolValueContext[SDV_TYPE]:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def name__sym_ref_syntax(self) -> str:
        return symbol_syntax.symbol_reference_syntax_for_name(self._name)

    @property
    def sdv(self) -> SDV_TYPE:
        return self.value.sdv

    @property
    def symbol_table_container(self) -> SymbolContainer:
        return self.value.container

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolTable({
            self.name: self.symbol_table_container
        })

    def reference(self, restrictions: ReferenceRestrictions) -> SymbolReference:
        return SymbolReference(self.name, restrictions)

    @property
    def definition(self) -> SymbolDefinition:
        return SymbolDefinition(self.name, self.value.container)

    @property
    def entry(self) -> Entry:
        return Entry(self.name, self.value.container)

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return self.value.reference_assertion(self._name)

    @property
    def usage_assertion(self) -> ValueAssertion[SymbolUsage]:
        return self.value.reference_assertion(self._name)

    @property
    def references_assertion(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence([
            self.reference_assertion,
        ])

    @property
    def usages_assertion(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence([
            self.usage_assertion,
        ])

    @staticmethod
    def symbol_table_of_contexts(symbols: Sequence['SymbolContext']) -> SymbolTable:
        return SymbolTable({
            symbol.name: symbol.symbol_table_container
            for symbol in symbols
        })

    @staticmethod
    def references_assertion_of_contexts(symbols: Sequence['SymbolContext']
                                         ) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence([
            context.reference_assertion
            for context in symbols
        ])

    @staticmethod
    def usages_assertion_of_contexts(symbols: Sequence['SymbolContext']) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence([
            symbol.usage_assertion
            for symbol in symbols
        ])

    @property
    def argument(self) -> ArgumentElementsRenderer:
        return args.SymbolReferenceWReferenceSyntax(self.name)
