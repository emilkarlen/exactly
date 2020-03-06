from abc import ABC, abstractmethod
from typing import Dict, Sequence, List, TypeVar, Generic

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeStv
from exactly_lib.symbol.sdv_structure import SymbolDependentTypeValue, SymbolContainer, SymbolUsage, SymbolReference
from exactly_lib.util import symbol_table
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import Entry, SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SymbolsArrEx:
    def __init__(self,
                 symbols_in_arrangement: Dict[str, SymbolDependentTypeValue],
                 expected_references: Sequence[ValueAssertion[SymbolReference]] = (),
                 ):
        self.symbols_in_arrangement = symbols_in_arrangement
        self.expected_references = expected_references

    @staticmethod
    def of_navs(
            symbols_in_arrangement: Sequence[NameAndValue[SymbolDependentTypeValue]],
            expected_references: Sequence[ValueAssertion[SymbolReference]] = (),
    ) -> 'SymbolsArrEx':
        return SymbolsArrEx(
            {
                nav.name: nav.value
                for nav in symbols_in_arrangement
            },
            expected_references,
        )

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
            Entry(symbol_name,
                  symbol_utils.container(sdv))
            for symbol_name, sdv in self.symbols_in_arrangement.items()
        ]

    @staticmethod
    def empty():
        return SymbolsArrEx({}, ())

    @property
    def symbol_table(self) -> SymbolTable:
        return self.table_with_additional_entries(())

    def table_with_additional_entries(self, additional: Sequence[Entry]) -> SymbolTable:
        entries = list(additional)
        entries += self.symbol_entries_for_arrangement

        return symbol_table.symbol_table_with_entries(entries)

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


STV_TYPE = TypeVar('STV_TYPE', bound=LogicTypeStv)


class SdvSymbolContext(Generic[STV_TYPE], ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    @abstractmethod
    def sdtv(self) -> STV_TYPE:
        pass

    @property
    def symbol_table_container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def name_and_sdtv(self) -> NameAndValue[STV_TYPE]:
        return NameAndValue(self.name,
                            self.sdtv)

    @property
    def name_and_container(self) -> NameAndValue[SymbolContainer]:
        return NameAndValue(self.name,
                            self.symbol_table_container)

    @property
    @abstractmethod
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        pass

    @property
    def references_assertion(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence([
            self.reference_assertion,
        ])

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolTable({
            self.name: self.symbol_table_container
        })

    def symbol_table__w_name(self, custom_name: str) -> SymbolTable:
        return SymbolTable({
            custom_name: self.symbol_table_container
        })

    @staticmethod
    def symbol_table_of_contexts(symbols: Sequence['SdvSymbolContext']) -> SymbolTable:
        return SymbolTable({
            symbol.name: symbol.symbol_table_container
            for symbol in symbols
        })
