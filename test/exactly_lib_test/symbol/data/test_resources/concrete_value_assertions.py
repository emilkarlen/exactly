import unittest
from typing import Sequence

from exactly_lib.symbol.data.impl.string_resolver_impls import ConstantStringFragmentResolver, \
    SymbolStringFragmentResolver
from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver, StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.test_resources.assertion_utils import \
    symbol_table_with_values_matching_references
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources import resolver_assertions
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase
from exactly_lib_test.type_system.data.test_resources.path_assertions import equals_path
from exactly_lib_test.type_system.data.test_resources.string_ddv_assertions import equals_string_ddv, \
    equals_string_fragment_ddv


def equals_path_resolver(expected: PathResolver) -> ValueAssertion:
    symbols = symbol_table_with_values_matching_references(expected.references)
    expected_path = expected.resolve(symbols)
    return resolver_assertions.matches_resolver_of_path(equals_symbol_references(expected.references),
                                                        equals_path(expected_path),
                                                        symbols=symbols)


def matches_path_resolver(expected_resolved_value: PathDdv,
                          expected_symbol_references: ValueAssertion,
                          symbol_table: SymbolTable = None) -> ValueAssertion:
    return resolver_assertions.matches_resolver_of_path(expected_symbol_references,
                                                        equals_path(expected_resolved_value),
                                                        symbols=symbol_table)


def equals_string_fragment_resolver_with_exact_type(expected: StringFragmentResolver) -> ValueAssertion:
    if isinstance(expected, ConstantStringFragmentResolver):
        return _EqualsStringFragmentAssertionForStringConstant(expected)
    if isinstance(expected, SymbolStringFragmentResolver):
        return _EqualsStringFragmentAssertionForSymbolReference(expected)
    raise TypeError('Not a StringFragmentResolver: ' + str(expected))


def equals_string_fragment_resolver(expected: StringFragmentResolver) -> ValueAssertion[StringFragmentResolver]:
    return _EqualsStringFragmentAssertion(expected)


def equals_string_fragments(expected_fragments) -> ValueAssertion:
    if isinstance(expected_fragments, list):
        expected_fragments = tuple(expected_fragments)
    return _EqualsStringFragments(expected_fragments)


def equals_string_resolver(expected: StringResolver,
                           symbols: SymbolTable = None) -> ValueAssertion[SymbolValueResolver]:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(expected.references)

    expected_resolved_value = expected.resolve(symbols)

    def get_fragment_resolvers(x: StringResolver) -> Sequence[StringFragmentResolver]:
        return x.fragments

    return resolver_assertions.matches_resolver_of_string(equals_symbol_references(expected.references),
                                                          equals_string_ddv(expected_resolved_value),
                                                          asrt.sub_component('fragment resolvers',
                                                                             get_fragment_resolvers,
                                                                             equals_string_fragments(
                                                                                 expected.fragments)),

                                                          symbols)


class _EqualsStringFragmentAssertionForStringConstant(ValueAssertionBase):
    def __init__(self, expected: ConstantStringFragmentResolver):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, ConstantStringFragmentResolver)
        assert isinstance(value, ConstantStringFragmentResolver)  # Type info for IDE

        put.assertTrue(value.is_string_constant,
                       message_builder.apply('is_string_constant'))

        put.assertEqual(self.expected.string_constant,
                        value.string_constant,
                        message_builder.apply('string_constant'))


class _EqualsStringFragmentAssertionForSymbolReference(ValueAssertionBase):
    def __init__(self, expected: SymbolStringFragmentResolver):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, SymbolStringFragmentResolver)
        assert isinstance(value, SymbolStringFragmentResolver)  # Type info for IDE

        put.assertFalse(value.is_string_constant,
                        'is_string_constant')

        put.assertEqual(self.expected.symbol_name,
                        value.symbol_name,
                        'symbol_name')


class _EqualsStringFragmentAssertion(ValueAssertionBase[StringFragmentResolver]):
    def __init__(self,
                 expected: StringFragmentResolver):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, StringFragmentResolver)
        assert isinstance(value, StringFragmentResolver)  # Type info for IDE
        symbols = symbol_table_with_values_matching_references(self.expected.references)
        tcds = fake_home_and_sds()
        environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)

        assertions = [
            asrt.sub_component('type_category',
                               lambda sfr: sfr.type_category,
                               asrt.equals(self.expected.type_category)
                               ),
            asrt.sub_component('data_value_type',
                               lambda sfr: sfr.data_value_type,
                               asrt.equals(self.expected.data_value_type)
                               ),
            asrt.sub_component('value_type',
                               lambda sfr: sfr.value_type,
                               asrt.equals(self.expected.value_type)
                               ),
            asrt.sub_component('is_string_constant',
                               lambda sfr: sfr.is_string_constant,
                               asrt.equals(self.expected.is_string_constant)
                               ),
            asrt.sub_component('resolve',
                               lambda sfr: sfr.resolve(environment.symbols),
                               equals_string_fragment_ddv(self.expected.resolve(environment.symbols))
                               ),

            asrt.sub_component('resolve_value_of_any_dependency',
                               lambda sfr: sfr.resolve_value_of_any_dependency(environment),
                               asrt.equals(
                                   self.expected.resolve_value_of_any_dependency(environment))
                               ),
        ]

        if self.expected.is_string_constant:
            assertions.append(
                asrt.sub_component('string_constant',
                                   lambda sfr: sfr.string_constant,
                                   asrt.equals(self.expected.string_constant)
                                   )
            )

        assertion = asrt.and_(assertions)

        assertion.apply(put, value, message_builder)


class _EqualsStringFragments(ValueAssertionBase):
    def __init__(self, expected: tuple):
        self._expected = expected
        assert isinstance(expected, tuple), 'Value reference list must be a tuple'
        self._sequence_of_element_assertions = []
        for idx, element in enumerate(expected):
            assert isinstance(element, StringFragmentResolver), 'Element must be a StringFragment #' + str(idx)
            self._sequence_of_element_assertions.append(equals_string_fragment_resolver_with_exact_type(element))

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, tuple,
                             'Expects a tuple of StringFragments')
        asrt.matches_sequence(self._sequence_of_element_assertions).apply(put, value, message_builder)
