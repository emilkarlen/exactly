from abc import ABC, abstractmethod
from typing import Sequence, List, TypeVar, Generic

from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.data.restrictions import reference_restrictions
from exactly_lib.symbol.sdv_structure import SymbolDependentTypeValue, SymbolContainer, SymbolUsage, SymbolReference, \
    ReferenceRestrictions, SymbolDefinition
from exactly_lib.util import symbol_table
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import Entry, SymbolTable
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as \
    asrt_rest
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

STV_TYPE = TypeVar('STV_TYPE', bound=SymbolDependentTypeValue)


class SymbolValueContext(Generic[STV_TYPE], ABC):
    def __init__(self, sdtv: STV_TYPE):
        self._sdtv = sdtv

    @property
    def sdtv(self) -> STV_TYPE:
        return self._sdtv

    @property
    def container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @abstractmethod
    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        pass


class DataSymbolValueContext(Generic[STV_TYPE], SymbolValueContext[STV_TYPE], ABC):
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


class LogicSymbolValueContext(Generic[STV_TYPE], SymbolValueContext[STV_TYPE], ABC):
    pass


class SymbolContext(Generic[STV_TYPE], ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    @abstractmethod
    def value(self) -> SymbolValueContext[STV_TYPE]:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def name__sym_ref_syntax(self) -> str:
        return symbol_syntax.symbol_reference_syntax_for_name(self._name)

    @property
    def sdtv(self) -> STV_TYPE:
        return self.value.sdtv

    @property
    def symbol_table_container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def container__of_builtin(self) -> SymbolContainer:
        return symbol_utils.container_of_builtin(self.sdtv)

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolTable({
            self.name: self.symbol_table_container
        })

    def symbol_table__w_name(self, custom_name: str) -> SymbolTable:
        return SymbolTable({
            custom_name: self.symbol_table_container
        })

    @property
    def name_and_sdtv(self) -> NameAndValue[STV_TYPE]:
        return NameAndValue(self.name,
                            self.sdtv)

    @property
    def name_and_container(self) -> NameAndValue[SymbolContainer]:
        return NameAndValue(self.name,
                            self.symbol_table_container)

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


class DataTypeSymbolContext(Generic[STV_TYPE], SymbolContext[STV_TYPE], ABC):
    def __init__(self,
                 name: str,
                 value: DataSymbolValueContext[STV_TYPE],
                 ):
        super().__init__(name)
        self._type_context = value

    @property
    def value(self) -> DataSymbolValueContext[STV_TYPE]:
        return self._type_context

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


class LogicTypeSymbolContext(Generic[STV_TYPE], SymbolContext[STV_TYPE], ABC):
    def __init__(self,
                 name: str,
                 value: LogicSymbolValueContext[STV_TYPE],
                 ):
        super().__init__(name)
        self.__type_context = value

    @property
    def value(self) -> LogicSymbolValueContext[STV_TYPE]:
        return self.__type_context


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
