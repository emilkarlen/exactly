import unittest

from exactly_lib.symbol import string_resolver as sut
from exactly_lib.type_system_values import string_value as sv, concrete_string_values as csv, file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_string_fragments
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.type_system_values.test_resources import string_value as asrt_sv
from exactly_lib_test.type_system_values.test_resources.string_value import equals_string_fragment


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstantStringFragmentResolver),
        unittest.makeSuite(TestSymbolStringFragmentResolver),
        unittest.makeSuite(StringResolverTest),
    ])


class TestConstantStringFragmentResolver(unittest.TestCase):
    string_constant = 'string constant'
    fragment = sut.ConstantStringFragmentResolver(string_constant)

    def test_should_be_string_constant(self):
        self.assertTrue(self.fragment.is_string_constant)

    def test_should_have_no_references(self):
        self.assertEqual((),
                         self.fragment.references)

    def test_string_constant(self):
        string_constant = 'string constant'
        fragment = sut.ConstantStringFragmentResolver(string_constant)
        self.assertEqual(string_constant,
                         fragment.string_constant)

    def test_resolve_should_give_string_constant(self):
        # ARRANGE #
        string_constant = 'string constant'
        fragment = sut.ConstantStringFragmentResolver(string_constant)
        # ACT #
        actual = fragment.resolve(empty_symbol_table())
        # ASSERT #
        assertion = equals_string_fragment(csv.ConstantFragment(string_constant))
        assertion.apply_without_message(self, actual)


class TestSymbolStringFragmentResolver(unittest.TestCase):
    def test_should_be_string_constant(self):
        fragment = sut.SymbolStringFragmentResolver(symbol_utils.symbol_reference('the_symbol_name'))
        self.assertFalse(fragment.is_string_constant)

    def test_should_have_exactly_one_references(self):
        # ARRANGE #
        symbol_reference = symbol_utils.symbol_reference('the_symbol_name')
        fragment = sut.SymbolStringFragmentResolver(symbol_reference)
        # ACT #
        actual = list(fragment.references)
        # ASSERT #
        assertion = equals_symbol_references([symbol_reference])
        assertion.apply_without_message(self, actual)

    def test_string_constant_SHOULD_raise_exception(self):
        fragment = sut.SymbolStringFragmentResolver(symbol_utils.symbol_reference('the_symbol_name'))
        with self.assertRaises(ValueError):
            fragment.string_constant

    def test_resolve_of_string_symbol_SHOULD_give_string_constant(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name', 'the symbol value')
        symbol_reference = symbol_utils.symbol_reference(symbol.name)
        fragment = sut.SymbolStringFragmentResolver(symbol_reference)
        symbol_table = symbol_utils.symbol_table_with_single_string_value(symbol.name, symbol.value)
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        assertion = equals_string_fragment(csv.ConstantFragment(symbol.value))
        assertion.apply_without_message(self, actual)

    def test_resolve_of_path_symbol_SHOULD_give_string_constant(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name',
                              file_refs.rel_act(PathPartAsFixedPath('file-name')))
        symbol_reference = symbol_utils.symbol_reference(symbol.name)
        fragment = sut.SymbolStringFragmentResolver(symbol_reference)
        symbol_table = symbol_utils.symbol_table_with_single_file_ref_value(symbol.name, symbol.value)
        # ACT #
        actual = fragment.resolve(symbol_table)
        # ASSERT #
        assertion = equals_string_fragment(csv.FileRefFragment(symbol.value))
        assertion.apply_without_message(self, actual)


class StringResolverTest(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        resolver = resolver_with_single_constant_fragment('value')
        # ACT #
        actual = resolver.value_type
        # ASSERT #
        self.assertIs(ValueType.STRING,
                      actual)

    def test_resolved_value(self):
        # ARRANGE #
        string_value = 'value'
        resolver = resolver_with_single_constant_fragment(string_value)
        # ACT #
        actual = resolver.resolve(empty_symbol_table())
        # ASSERT #
        assertion = asrt_sv.equals_string_value(sv.StringValue((csv.ConstantFragment(string_value),)))
        assertion.apply_without_message(self, actual)

    def test_fragments(self):
        # ARRANGE #
        fragment_value = 'value'
        resolver = resolver_with_single_constant_fragment(fragment_value)
        # ACT #
        actual = resolver.fragments
        # ASSERT #
        assertion = equals_string_fragments([sut.ConstantStringFragmentResolver(fragment_value)])
        assertion.apply_without_message(self, actual)


def resolver_with_single_constant_fragment(fragment_value: str) -> sut.StringResolver:
    return sut.StringResolver((sut.ConstantStringFragmentResolver(fragment_value),))
