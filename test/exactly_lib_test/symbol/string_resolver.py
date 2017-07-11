import unittest

from exactly_lib.symbol import string_resolver as sut
from exactly_lib.type_system_values import string_value as sv, concrete_string_values as csv
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_string_fragments
from exactly_lib_test.type_system_values.test_resources import string_value as asrt_sv
from exactly_lib_test.type_system_values.test_resources.string_value import equals_string_fragment


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstantStringFragmentResolver),
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
