from typing import Dict, Sequence, List

from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.util import symbol_table
from exactly_lib.util.symbol_table import Entry, SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SymbolsArrAndExpectSetup:
    def __init__(self,
                 symbols_in_arrangement: Dict[str, SymbolValueResolver],
                 expected_references: Sequence[ValueAssertion[SymbolUsage]] = ()):
        self.symbols_in_arrangement = symbols_in_arrangement
        self.expected_references = expected_references

    @property
    def expected_references_list(self) -> List[ValueAssertion[SymbolUsage]]:
        return list(self.expected_references)

    @property
    def symbol_entries_for_arrangement(self) -> List[Entry]:
        return [
            Entry(symbol_name,
                  symbol_utils.container(resolver))
            for symbol_name, resolver in self.symbols_in_arrangement.items()
        ]

    @staticmethod
    def empty():
        return SymbolsArrAndExpectSetup({}, ())

    def table_with_additional_entries(self, additional: Sequence[Entry]) -> SymbolTable:
        entries = list(additional)
        entries += self.symbol_entries_for_arrangement

        return symbol_table.symbol_table_with_entries(entries)

    def matches_preceded_by(self, precedes: Sequence[ValueAssertion[SymbolUsage]]
                            ) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(
            list(precedes) +
            self.expected_references_list
        )
