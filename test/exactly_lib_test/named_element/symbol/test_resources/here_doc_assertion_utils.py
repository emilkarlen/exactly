from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol.restrictions import reference_restrictions
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.named_element.symbol.test_resources.any_resolver_assertions import \
    MatchesPrimitiveValueResolvedOfAnyDependency
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def reference_to(symbol: NameAndValue) -> NamedElementReference:
    return NamedElementReference(symbol.name,
                                 reference_restrictions.no_restrictions())


def contents_str_from_lines(lines_of_here_doc: list) -> str:
    return lines_content(lines_of_here_doc)


def matches_resolved_value(expected_resolved_primitive_lines: list,
                           symbol_references: list = None,
                           symbols: SymbolTable = None) -> asrt.ValueAssertion:
    symbols = empty_symbol_table() if symbols is None else symbols
    symbol_references = [] if symbol_references is None else symbol_references
    return MatchesPrimitiveValueResolvedOfAnyDependency(
        asrt.equals(contents_str_from_lines(expected_resolved_primitive_lines)),
        symbol_references,
        symbols)
