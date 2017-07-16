import unittest

from exactly_lib.symbol import concrete_resolvers
from exactly_lib.symbol import list_resolver
from exactly_lib.symbol.list_resolver import ListResolver
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.type_system_values.list_value import ListValue
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.symbol.test_resources.assertion_utils import symbol_table_with_values_matching_references
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import _EqualsSymbolValueResolverBase
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references, \
    equals_symbol_reference
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system_values.test_resources.list_value import equals_list_value
from exactly_lib_test.type_system_values.test_resources.string_value import equals_string_value


def equals_list_resolver_element(expected: list_resolver.Element,
                                 symbols: SymbolTable = None) -> asrt.ValueAssertion:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(list(expected.references))
    expected_resolved_value_list = expected.resolve(symbols)
    assertion_on_resolved_value = asrt.matches_sequence(
        [equals_string_value(sv) for sv in expected_resolved_value_list])
    component_assertions = [
        asrt.sub_component('references',
                           lambda x: list(x.references),
                           equals_symbol_references(list(expected.references))),
        asrt.sub_component('resolved value',
                           lambda x: x.resolve(symbols),
                           assertion_on_resolved_value),

    ]
    symbol_reference_assertion = asrt.is_none
    if expected.symbol_reference_if_is_symbol_reference is not None:
        symbol_reference_assertion = equals_symbol_reference(expected.symbol_reference_if_is_symbol_reference)
    symbol_reference_component_assertion = asrt.sub_component('symbol_reference_if_is_symbol_reference',
                                                              lambda x: x.symbol_reference_if_is_symbol_reference,
                                                              symbol_reference_assertion)
    component_assertions.append(symbol_reference_component_assertion)
    return asrt.is_instance_with(
        list_resolver.Element,
        asrt.and_(component_assertions))


def equals_list_resolver_elements(elements: list,
                                  symbols: SymbolTable = None) -> asrt.ValueAssertion:
    element_assertions = [equals_list_resolver_element(element, symbols)
                          for element in elements]
    return asrt.matches_sequence(element_assertions)


def equals_list_resolver(expected: ListResolver,
                         symbols: SymbolTable = None) -> asrt.ValueAssertion:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(expected.references)
    assertion_on_symbol_references = equals_symbol_references(expected.references)

    return _EqualsListValueResolverAssertion(assertion_on_symbol_references,
                                             expected,
                                             symbols)


def matches_list_resolver(expected_resolved_value: ListValue,
                          expected_symbol_references: asrt.ValueAssertion,
                          symbols: SymbolTable = None) -> asrt.ValueAssertion:
    if symbols is None:
        symbols = empty_symbol_table()

    return _MatchesListValueResolverAssertion(expected_symbol_references,
                                              expected_resolved_value,
                                              symbols)


def equals_constant_list(expected_str_list: list) -> asrt.ValueAssertion:
    return equals_list_resolver(concrete_resolvers.list_constant(expected_str_list))


class _EqualsListValueResolverAssertion(_EqualsSymbolValueResolverBase):
    def __init__(self,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolver: ListResolver,
                 symbols_for_checking_resolving: SymbolTable):
        super().__init__(ValueType.LIST,
                         expected_symbol_references,
                         equals_list_value(expected_resolver.resolve(symbols_for_checking_resolving)),
                         symbols_for_checking_resolving)
        self._expected_resolver = expected_resolver

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: SymbolValueResolver,
                                  message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, ListResolver,
                             'Actual value is expected to be a ' + str(ListResolver))
        assert isinstance(actual, ListResolver)
        elements_assertion = equals_list_resolver_elements(list(self._expected_resolver.elements))
        elements_assertion.apply(put, actual.elements,
                                 message_builder.for_sub_component('elements'))


class _MatchesListValueResolverAssertion(_EqualsSymbolValueResolverBase):
    def __init__(self,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolved_value: ListValue,
                 symbols_for_checking_resolving: SymbolTable):
        super().__init__(ValueType.LIST,
                         expected_symbol_references,
                         equals_list_value(expected_resolved_value),
                         symbols_for_checking_resolving)

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: SymbolValueResolver,
                                  message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, ListResolver,
                             'Actual value is expected to be a ' + str(ListResolver))
