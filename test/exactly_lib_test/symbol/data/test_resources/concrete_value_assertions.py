import unittest

from exactly_lib.help_texts import type_system
from exactly_lib.symbol.data.string_resolvers import ConstantStringFragmentResolver, \
    SymbolStringFragmentResolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver, StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.value_type import DataValueType, TypeCategory
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.symbol.data.test_resources.assertion_utils import \
    symbol_table_with_values_matching_references
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.file_ref_assertions import equals_file_ref
from exactly_lib_test.type_system.data.test_resources.string_value_assertions import equals_string_value, \
    equals_string_fragment


def equals_file_ref_resolver(expected: FileRefResolver) -> asrt.ValueAssertion:
    symbols = symbol_table_with_values_matching_references(expected.references)
    expected_file_ref = expected.resolve(symbols)
    assertion_on_resolved_value = equals_file_ref(expected_file_ref)
    assertion_on_symbol_references = equals_symbol_references(expected.references)
    return _FileRefResolverAssertion(assertion_on_symbol_references,
                                     assertion_on_resolved_value,
                                     symbols)


def matches_file_ref_resolver(expected_resolved_value: FileRef,
                              expected_symbol_references: asrt.ValueAssertion,
                              symbol_table: SymbolTable = None) -> asrt.ValueAssertion:
    if symbol_table is None:
        symbol_table = empty_symbol_table()
    assertion_on_resolved_value = equals_file_ref(expected_resolved_value)
    return _FileRefResolverAssertion(expected_symbol_references,
                                     assertion_on_resolved_value,
                                     symbol_table)


def equals_string_fragment_resolver_with_exact_type(expected: StringFragmentResolver) -> asrt.ValueAssertion:
    if isinstance(expected, ConstantStringFragmentResolver):
        return _EqualsStringFragmentAssertionForStringConstant(expected)
    if isinstance(expected, SymbolStringFragmentResolver):
        return _EqualsStringFragmentAssertionForSymbolReference(expected)
    raise TypeError('Not a StringFragmentResolver: ' + str(expected))


def equals_string_fragment_resolver(expected: StringFragmentResolver) -> asrt.ValueAssertion[StringFragmentResolver]:
    return _EqualsStringFragmentAssertion(expected)


def equals_string_fragments(expected_fragments) -> asrt.ValueAssertion:
    if isinstance(expected_fragments, list):
        expected_fragments = tuple(expected_fragments)
    return _EqualsStringFragments(expected_fragments)


def equals_string_resolver(expected: StringResolver,
                           symbols: SymbolTable = None) -> asrt.ValueAssertion:
    if symbols is None:
        symbols = symbol_table_with_values_matching_references(expected.references)
    expected_resolved_value = expected.resolve(symbols)
    assertion_on_resolved_value = equals_string_value(expected_resolved_value)
    assertion_on_symbol_references = equals_symbol_references(expected.references)
    assertion_on_fragments = equals_string_fragments(expected.fragments)

    return _StringValueResolverAssertion(assertion_on_symbol_references,
                                         assertion_on_resolved_value,
                                         assertion_on_fragments,
                                         symbols)


class _EqualsSymbolValueResolverBase(asrt.ValueAssertion):
    def __init__(self,
                 expected_data_value_type: DataValueType,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolved_value: asrt.ValueAssertion,
                 symbols_for_checking_resolving: SymbolTable):
        self.expected_data_value_type = expected_data_value_type
        self.expected_symbol_references = expected_symbol_references
        self.expected_resolved_value = expected_resolved_value
        self.symbols_for_checking_resolving = symbols_for_checking_resolving

    def apply(self,
              put: unittest.TestCase,
              actual,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(actual, DataValueResolver,
                             message_builder.apply('object type'))
        assert isinstance(actual, DataValueResolver)  # Type info for IDE

        self.assert_type_is_expected(put, actual, message_builder)

        self.expected_symbol_references.apply(put, actual.references,
                                              message_builder.for_sub_component('symbol_references'))

        self._custom_check_of_resolver(put, actual, message_builder)

        resolved_value = actual.resolve(self.symbols_for_checking_resolving)

        put.assertIsInstance(resolved_value, DirDependentValue,
                             message_builder.apply('object type of resolved value'))

        self.expected_resolved_value.apply(put, resolved_value,
                                           message_builder.for_sub_component('resolved value'))

    def assert_type_is_expected(self,
                                put: unittest.TestCase,
                                actual: DataValueResolver,
                                message_builder: asrt.MessageBuilder):
        put.assertIs(TypeCategory.DATA,
                     actual.type_category,
                     'element_type')
        put.assertIs(self.expected_data_value_type,
                     actual.data_value_type,
                     message_builder.apply('data_value_type'))

        expected_value_type = type_system.DATA_TYPE_2_VALUE_TYPE[self.expected_data_value_type]

        put.assertIs(expected_value_type,
                     actual.value_type,
                     message_builder.apply('value_type'))

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: DataValueResolver,
                                  message_builder: asrt.MessageBuilder):
        pass


class _EqualsStringFragmentAssertionForStringConstant(asrt.ValueAssertion):
    def __init__(self, expected: ConstantStringFragmentResolver):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, ConstantStringFragmentResolver)
        assert isinstance(value, ConstantStringFragmentResolver)  # Type info for IDE

        put.assertTrue(value.is_string_constant,
                       'is_string_constant')

        put.assertEqual(self.expected.string_constant,
                        value.string_constant,
                        'string_constant')


class _EqualsStringFragmentAssertionForSymbolReference(asrt.ValueAssertion):
    def __init__(self, expected: SymbolStringFragmentResolver):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, SymbolStringFragmentResolver)
        assert isinstance(value, SymbolStringFragmentResolver)  # Type info for IDE

        put.assertFalse(value.is_string_constant,
                        'is_string_constant')

        put.assertEqual(self.expected.symbol_name,
                        value.symbol_name,
                        'symbol_name')


class _EqualsStringFragmentAssertion(asrt.ValueAssertion[StringFragmentResolver]):
    def __init__(self,
                 expected: StringFragmentResolver):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
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
                               equals_string_fragment(self.expected.resolve(environment.symbols))
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


class _EqualsStringFragments(asrt.ValueAssertion):
    def __init__(self, expected: tuple):
        self._expected = expected
        assert isinstance(expected, tuple), 'Value reference list must be a tuple'
        self._sequence_of_element_assertions = []
        for idx, element in enumerate(expected):
            assert isinstance(element, StringFragmentResolver), 'Element must be a StringFragment #' + str(idx)
            self._sequence_of_element_assertions.append(equals_string_fragment_resolver_with_exact_type(element))

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, tuple,
                             'Expects a tuple of StringFragments')
        asrt.matches_sequence(self._sequence_of_element_assertions).apply(put, value, message_builder)


class _FileRefResolverAssertion(_EqualsSymbolValueResolverBase):
    def __init__(self,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolved_value: asrt.ValueAssertion,
                 symbols_for_checking_resolving: SymbolTable):
        super().__init__(DataValueType.PATH,
                         expected_symbol_references,
                         expected_resolved_value,
                         symbols_for_checking_resolving)

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: DataValueResolver,
                                  message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, FileRefResolver,
                             message_builder.apply('Actual value is expected to be a ' + str(FileRefResolver)))


class _StringValueResolverAssertion(_EqualsSymbolValueResolverBase):
    def __init__(self,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolved_value: asrt.ValueAssertion,
                 expected_string_fragments: asrt.ValueAssertion,
                 symbols_for_checking_resolving: SymbolTable):
        super().__init__(DataValueType.STRING,
                         expected_symbol_references,
                         expected_resolved_value,
                         symbols_for_checking_resolving)
        self._expected_string_fragments = expected_string_fragments

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: DataValueResolver,
                                  message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, StringResolver,
                             'Actual value is expected to be a ' + str(StringResolver))
        assert isinstance(actual, StringResolver)

        self._expected_string_fragments.apply(put, actual.fragments,
                                              message_builder.for_sub_component('fragments'))
