from abc import ABC, abstractmethod
from typing import Sequence, List, TypeVar, Generic, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.data.restrictions import reference_restrictions
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolUsage, SymbolReference, \
    ReferenceRestrictions, SymbolDefinition, SymbolDependentValue
from exactly_lib.type_system.value_type import ValueType, DataValueType
from exactly_lib.util import line_source
from exactly_lib.util import symbol_table
from exactly_lib.util.symbol_table import Entry, SymbolTable
from exactly_lib_test.section_document.test_resources import source_location
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as \
    asrt_rest
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.container_assertions import matches_container_of_data_type
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_definition
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

SDV_TYPE = TypeVar('SDV_TYPE', bound=SymbolDependentValue)

MODEL = TypeVar('MODEL')

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


class DataSymbolValueContext(Generic[SDV_TYPE], SymbolValueContext[SDV_TYPE], ABC):
    def __init__(self,
                 sdv: SDV_TYPE,
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)

    @property
    @abstractmethod
    def data_value_type(self) -> DataValueType:
        pass

    @staticmethod
    def reference_assertion__any_data_type(symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(
            symbol_name,
            asrt_rest.is_any_data_type_reference_restrictions()
        )

    @staticmethod
    def usage_assertion__any_data_type(symbol_name: str) -> ValueAssertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference_2(
            symbol_name,
            asrt_rest.is_any_data_type_reference_restrictions()
        )

    @property
    def assert_matches_container_of_sdv(self) -> ValueAssertion[SymbolContainer]:
        return matches_container_of_data_type(
            data_value_type=self.data_value_type,
            sdv=self.assert_equals_sdv,
            definition_source=asrt.anything_goes()
        )

    @property
    @abstractmethod
    def assert_equals_sdv(self) -> ValueAssertion[SymbolDependentValue]:
        pass


class LogicSymbolValueContext(Generic[SDV_TYPE], SymbolValueContext[SDV_TYPE], ABC):
    def __init__(self,
                 sdv: SDV_TYPE,
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)


class MatcherSymbolValueContext(Generic[MODEL], LogicSymbolValueContext[MatcherSdv[MODEL]], ABC):
    def __init__(self,
                 sdv: MatcherSdv[MODEL],
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)


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
    def references_assertion(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence([
            self.reference_assertion,
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


class DataTypeSymbolContext(Generic[SDV_TYPE], SymbolContext[SDV_TYPE], ABC):
    def __init__(self, name: str, ):
        super().__init__(name)

    @property
    @abstractmethod
    def value(self) -> DataSymbolValueContext[SDV_TYPE]:
        pass

    @property
    def reference__any_data_type(self) -> SymbolReference:
        return SymbolReference(
            self.name,
            reference_restrictions.is_any_data_type()
        )

    @property
    def reference_assertion__any_data_type(self) -> ValueAssertion[SymbolReference]:
        return DataSymbolValueContext.reference_assertion__any_data_type(self.name)

    @property
    def usage_assertion__any_data_type(self) -> ValueAssertion[SymbolUsage]:
        return DataSymbolValueContext.usage_assertion__any_data_type(self.name)

    @property
    def assert_matches_definition_of_sdv(self) -> ValueAssertion[SymbolDefinition]:
        return matches_definition(
            name=asrt.equals(self.name),
            container=self.value.assert_matches_container_of_sdv
        )


class LogicTypeSymbolContext(Generic[SDV_TYPE], SymbolContext[SDV_TYPE], ABC):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    @abstractmethod
    def value(self) -> LogicSymbolValueContext[SDV_TYPE]:
        pass


class MatcherTypeSymbolContext(Generic[MODEL], LogicTypeSymbolContext[MatcherSdv[MODEL]], ABC):
    def __init__(self,
                 name: str,
                 value: MatcherSymbolValueContext[MODEL],
                 ):
        super().__init__(name)
        self._value = value

    @property
    def value(self) -> MatcherSymbolValueContext[MODEL]:
        return self._value


class SymbolsArrEx:
    def __init__(self,
                 symbols_in_arrangement: List[SymbolContext],
                 expected_references: Sequence[ValueAssertion[SymbolReference]] = (),
                 ):
        self.symbols_in_arrangement = symbols_in_arrangement
        self.expected_references = expected_references

    @property
    def expected_references_list(self) -> List[ValueAssertion[SymbolReference]]:
        return list(self.expected_references)

    @property
    def expected_references_assertion(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence(self.expected_references_list)

    @property
    def expected_usages_list(self) -> List[ValueAssertion[SymbolUsage]]:
        return [
            asrt.is_instance_with(SymbolReference, sym_ref)
            for sym_ref in self.expected_references
        ]

    @property
    def expected_usages_assertion(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(self.expected_usages_list)

    @property
    def symbol_entries_for_arrangement(self) -> List[Entry]:
        return [
            symbol_context.entry
            for symbol_context in self.symbols_in_arrangement
        ]

    @staticmethod
    def empty():
        return SymbolsArrEx([], ())

    @property
    def symbol_table(self) -> SymbolTable:
        return self.table_with_additional_entries(())

    def table_with_additional_entries(self, additional: Sequence[Entry]) -> SymbolTable:
        entries = list(additional)
        entries += self.symbol_entries_for_arrangement

        return symbol_table.symbol_table_with_entries(entries)

    def table_with_additional_contexts(self, additional: Sequence[SymbolContext]) -> SymbolTable:
        contexts = list(additional)
        contexts += self.symbol_entries_for_arrangement

        return SymbolContext.symbol_table_of_contexts(contexts)

    def matches_references_preceded_by(self, precedes: Sequence[ValueAssertion[SymbolReference]]
                                       ) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(
            list(precedes) +
            self.expected_references_list
        )

    def matches_usages_preceded_by(self, precedes: Sequence[ValueAssertion[SymbolUsage]]
                                   ) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(
            list(precedes) +
            self.expected_usages_list
        )
