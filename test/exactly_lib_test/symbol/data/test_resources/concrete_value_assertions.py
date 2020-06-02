import unittest
from typing import Sequence

from exactly_lib.symbol.data.impl.string_sdv_impls import ConstantStringFragmentSdv, \
    SymbolStringFragmentSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringFragmentSdv, StringSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.test_resources.assertion_utils import \
    symbol_table_with_values_matching_references
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_data_type_symbol_references
from exactly_lib_test.symbol.test_resources import sdv_type_assertions
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase
from exactly_lib_test.type_system.data.test_resources.path_assertions import equals_path
from exactly_lib_test.type_system.data.test_resources.string_ddv_assertions import equals_string_ddv, \
    equals_string_fragment_ddv


def equals_path_sdv(expected: PathSdv) -> ValueAssertion[SymbolDependentValue]:
    symbols = symbol_table_with_values_matching_references(expected.references)
    expected_path = expected.resolve(symbols)
    return sdv_type_assertions.matches_sdv_of_path(
        equals_data_type_symbol_references(expected.references),
        equals_path(expected_path),
        symbols=symbols)


def matches_path_sdv(expected_resolved_value: PathDdv,
                     expected_symbol_references: ValueAssertion,
                     symbol_table: SymbolTable = None) -> ValueAssertion[SymbolDependentValue]:
    return sdv_type_assertions.matches_sdv_of_path(expected_symbol_references,
                                                   equals_path(
                                                       expected_resolved_value),
                                                   symbols=symbol_table)


def equals_string_fragment_sdv_with_exact_type(expected: StringFragmentSdv) -> ValueAssertion[StringFragmentSdv]:
    if isinstance(expected, ConstantStringFragmentSdv):
        return _EqualsStringFragmentAssertionForStringConstant(expected)
    if isinstance(expected, SymbolStringFragmentSdv):
        return _EqualsStringFragmentAssertionForSymbolReference(expected)
    raise TypeError('Not a {}: {}'.format(StringFragmentSdv, expected))


def equals_string_fragment_sdv(expected: StringFragmentSdv) -> ValueAssertion[StringFragmentSdv]:
    return _EqualsStringFragmentAssertion(expected)


def equals_string_fragments(expected_fragments) -> ValueAssertion:
    if isinstance(expected_fragments, list):
        expected_fragments = tuple(expected_fragments)
    return _EqualsStringFragments(expected_fragments)


def equals_string_sdv(expected: StringSdv,
                      symbols: SymbolTable = None) -> ValueAssertion[SymbolDependentValue]:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(expected.references)

    expected_resolved_value = expected.resolve(symbols)

    def get_fragment_sdvs(x: StringSdv) -> Sequence[StringFragmentSdv]:
        return x.fragments

    return sdv_type_assertions.matches_sdv_of_string(
        equals_data_type_symbol_references(expected.references),
        equals_string_ddv(expected_resolved_value),
        asrt.sub_component('fragment resolvers',
                           get_fragment_sdvs,
                           equals_string_fragments(
                               expected.fragments)),

        symbols)


class _EqualsStringFragmentAssertionForStringConstant(ValueAssertionBase[StringFragmentSdv]):
    def __init__(self, expected: ConstantStringFragmentSdv):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, ConstantStringFragmentSdv)
        assert isinstance(value, ConstantStringFragmentSdv)  # Type info for IDE

        put.assertTrue(value.is_string_constant,
                       message_builder.apply('is_string_constant'))

        put.assertEqual(self.expected.string_constant,
                        value.string_constant,
                        message_builder.apply('string_constant'))


class _EqualsStringFragmentAssertionForSymbolReference(ValueAssertionBase[StringFragmentSdv]):
    def __init__(self, expected: SymbolStringFragmentSdv):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, SymbolStringFragmentSdv)
        assert isinstance(value, SymbolStringFragmentSdv)  # Type info for IDE

        put.assertFalse(value.is_string_constant,
                        message_builder.apply('is_string_constant'))

        put.assertEqual(self.expected.symbol_name,
                        value.symbol_name,
                        message_builder.apply('symbol_name'))


class _EqualsStringFragmentAssertion(ValueAssertionBase[StringFragmentSdv]):
    def __init__(self, expected: StringFragmentSdv):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: StringFragmentSdv,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, StringFragmentSdv)
        assert isinstance(value, StringFragmentSdv)  # Type info for IDE
        symbols = symbol_table_with_values_matching_references(self.expected.references)
        tcds = fake_tcds()
        environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)

        assertions = [
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
            assert isinstance(element, StringFragmentSdv), 'Element must be a StringFragment #' + str(idx)
            self._sequence_of_element_assertions.append(equals_string_fragment_sdv_with_exact_type(element))

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, tuple,
                             'Expects a tuple of StringFragments')
        asrt.matches_sequence(self._sequence_of_element_assertions).apply(put, value, message_builder)
