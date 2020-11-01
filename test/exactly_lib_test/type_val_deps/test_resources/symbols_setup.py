from typing import Sequence, List

from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.util import symbol_table
from exactly_lib.util.symbol_table import Entry, SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
