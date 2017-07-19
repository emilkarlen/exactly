from exactly_lib.symbol.restrictions import reference_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.symbol.test_resources.any_resolver_assertions import MatchesPrimitiveValueResolvedOfAnyDependency
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def reference_to(symbol: NameAndValue) -> SymbolReference:
    return SymbolReference(symbol.name,
                           reference_restrictions.no_restrictions())


def matches_resolved_value(expected_resolved_primitive_lines: list,
                           symbol_references: list = None,
                           symbols: SymbolTable = None) -> asrt.ValueAssertion:
    symbols = empty_symbol_table() if symbols is None else symbols
    symbol_references = [] if symbol_references is None else symbol_references
    return MatchesPrimitiveValueResolvedOfAnyDependency(
        asrt.equals(lines_content(expected_resolved_primitive_lines)),
        symbol_references,
        symbols)
