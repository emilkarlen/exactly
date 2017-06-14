import unittest

from exactly_lib.symbol import concrete_restrictions
from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.concrete_values import FileRefResolver, ValueVisitor
from exactly_lib.symbol.string_resolver import StringFragmentResolver, ConstantStringFragmentResolver, \
    SymbolStringFragmentResolver, StringResolver, string_constant
from exactly_lib.symbol.value_structure import ValueContainer, Value, SymbolValueResolver, ValueType
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.symbol_utils import file_ref_value
from exactly_lib_test.test_case_file_structure.test_resources.file_ref import equals_file_ref
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_case_file_structure.test_resources.string_value import equals_string_value
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolver_equals3(expected: SymbolValueResolver) -> asrt.ValueAssertion:
    return _EqualsValue(expected)


def file_ref_resolver_equals(expected: FileRefResolver) -> asrt.ValueAssertion:
    symbols = _symbol_table_with_values_matching_references(expected.references)
    expected_file_ref = expected.resolve(symbols)
    assertion_on_resolved_value = equals_file_ref(expected_file_ref)
    assertion_on_symbol_references = equals_symbol_references(expected.references)
    return _FileRefResolverAssertion(assertion_on_symbol_references,
                                     assertion_on_resolved_value,
                                     symbols)


def equals_file_ref_resolver2(expected_relativity_and_paths: FileRef,
                              expected_symbol_references: asrt.ValueAssertion,
                              symbol_table: SymbolTable = None) -> asrt.ValueAssertion:
    if symbol_table is None:
        symbol_table = empty_symbol_table()
    assertion_on_resolved_value = equals_file_ref(expected_relativity_and_paths)
    return _FileRefResolverAssertion(expected_symbol_references,
                                     assertion_on_resolved_value,
                                     symbol_table)


def equals_string_fragment(expected: StringFragmentResolver) -> asrt.ValueAssertion:
    if isinstance(expected, ConstantStringFragmentResolver):
        return _EqualsStringFragmentAssertionForStringConstant(expected)
    if isinstance(expected, SymbolStringFragmentResolver):
        return _EqualsStringFragmentAssertionForSymbolReference(expected)
    raise TypeError('Not a StringResolver: ' + str(expected))


def equals_string_fragments(expected_fragments) -> asrt.ValueAssertion:
    if isinstance(expected_fragments, list):
        expected_fragments = tuple(expected_fragments)
    return _EqualsStringFragments(expected_fragments)


def equals_string_resolver3(expected: StringResolver,
                            symbols: SymbolTable = None) -> asrt.ValueAssertion:
    if symbols is None:
        symbols = _symbol_table_with_values_matching_references(expected.references)
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
                 expected_value_type: ValueType,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolved_value: asrt.ValueAssertion,
                 symbols_for_checking_resolving: SymbolTable):
        self.expected_value_type = expected_value_type
        self.expected_symbol_references = expected_symbol_references
        self.expected_resolved_value = expected_resolved_value
        self.symbols_for_checking_resolving = symbols_for_checking_resolving

    def apply(self,
              put: unittest.TestCase,
              actual,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(actual, SymbolValueResolver,
                             message_builder.apply('object type'))
        assert isinstance(actual, SymbolValueResolver)  # Type info for IDE

        put.assertIs(self.expected_value_type,
                     actual.value_type,
                     message_builder.apply('value_type'))

        self.expected_symbol_references.apply(put, actual.references,
                                              message_builder.for_sub_component('symbol_references'))

        self._custom_check_of_resolver(put, actual, message_builder)

        resolved_value = actual.resolve(self.symbols_for_checking_resolving)

        put.assertIsInstance(resolved_value, DirDependentValue,
                             message_builder.apply('object type of resolved value'))

        self.expected_resolved_value.apply(put, resolved_value,
                                           message_builder.for_sub_component('resolved value'))

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: SymbolValueResolver,
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

        put.assertFalse(value.is_symbol,
                        'is_symbol')

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

        put.assertTrue(value.is_symbol,
                       'is_symbol')

        put.assertEqual(self.expected.symbol_name,
                        value.symbol_name,
                        'symbol_name')


class _EqualsStringFragments(asrt.ValueAssertion):
    def __init__(self, expected: tuple):
        self._expected = expected
        assert isinstance(expected, tuple), 'Value reference list must be a tuple'
        self._sequence_of_element_assertions = []
        for idx, element in enumerate(expected):
            assert isinstance(element, StringFragmentResolver), 'Element must be a StringFragment #' + str(idx)
            self._sequence_of_element_assertions.append(equals_string_fragment(element))

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
        super().__init__(ValueType.PATH,
                         expected_symbol_references,
                         expected_resolved_value,
                         symbols_for_checking_resolving)

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: SymbolValueResolver,
                                  message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, FileRefResolver,
                             message_builder.apply('Actual value is expected to be a ' + str(FileRefResolver)))


class _StringValueResolverAssertion(_EqualsSymbolValueResolverBase):
    def __init__(self,
                 expected_symbol_references: asrt.ValueAssertion,
                 expected_resolved_value: asrt.ValueAssertion,
                 expected_string_fragments: asrt.ValueAssertion,
                 symbols_for_checking_resolving: SymbolTable):
        super().__init__(ValueType.STRING,
                         expected_symbol_references,
                         expected_resolved_value,
                         symbols_for_checking_resolving)
        self._expected_string_fragments = expected_string_fragments

    def _custom_check_of_resolver(self,
                                  put: unittest.TestCase,
                                  actual: SymbolValueResolver,
                                  message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, StringResolver,
                             'Actual value is expected to be a ' + str(StringResolver))
        assert isinstance(actual, StringResolver)

        self._expected_string_fragments.apply(put, actual.fragments,
                                              message_builder.for_sub_component('fragments'))


def file_ref_val_test_impl(valid_relativities: PathRelativityVariants) -> FileRefResolver:
    relativity = list(valid_relativities.rel_option_types)[0]
    assert isinstance(relativity, RelOptionType)
    return file_ref_value(file_ref_test_impl('file_ref_test_impl', relativity))


def _value_container(value: FileRefResolver) -> ValueContainer:
    return ValueContainer(Line(1, 'source line'), value)


def _symbol_table_with_values_matching_references(references: list) -> SymbolTable:
    value_constructor = _ValueCorrespondingToValueRestriction()
    elements = {}
    for ref in references:
        assert isinstance(ref, su.SymbolReference), "Informs IDE of type"
        value_restriction = ref.restrictions.direct
        assert isinstance(value_restriction, concrete_restrictions.ValueRestriction)
        value = value_constructor.visit(value_restriction)
        elements[ref.name] = _value_container(value)
    return SymbolTable(elements)


class _ValueCorrespondingToValueRestriction(concrete_restrictions.ValueRestrictionVisitor):
    def visit_none(self, x: concrete_restrictions.NoRestriction) -> Value:
        return string_constant('a string (from <no restriction>)')

    def visit_string(self, x: concrete_restrictions.StringRestriction) -> Value:
        return string_constant('a string (from <string value restriction>)')

    def visit_file_ref_relativity(self, x: concrete_restrictions.FileRefRelativityRestriction) -> Value:
        return file_ref_val_test_impl(x.accepted)

    def visit_string_or_file_ref_relativity(self, x: concrete_restrictions.EitherStringOrFileRefRelativityRestriction
                                            ) -> Value:
        return self.visit_file_ref_relativity(x.file_ref_restriction)


class _EqualsValueVisitor(ValueVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def _visit_file_ref(self, expected: FileRefResolver):
        return file_ref_resolver_equals(expected).apply(self.put, self.actual, self.message_builder)

    def _visit_string(self, expected: StringResolver):
        return equals_string_resolver3(expected).apply(self.put, self.actual, self.message_builder)


class _EqualsValue(asrt.ValueAssertion):
    def __init__(self, expected: SymbolValueResolver):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsValueVisitor(value, put, message_builder).visit(self.expected)
