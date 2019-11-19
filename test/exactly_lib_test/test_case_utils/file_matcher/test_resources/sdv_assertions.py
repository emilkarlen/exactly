from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources import sdv_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def resolved_ddv_matches_file_matcher(ddv: ValueAssertion[FileMatcherDdv],
                                      references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                      symbols: symbol_table.SymbolTable = None
                                      ) -> ValueAssertion[SymbolDependentValue]:
    return sdv_assertions.matches_sdv_of_file_matcher(
        references,
        ddv,
        symbols=symbols)
