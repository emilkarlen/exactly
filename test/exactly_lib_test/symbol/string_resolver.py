import unittest

from exactly_lib.symbol import concrete_string_values as csv
from exactly_lib.symbol import string_resolver as sut
from exactly_lib.symbol import string_value as sv
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_string_fragments
from exactly_lib_test.test_case_file_structure.test_resources import string_value as asrt_sv


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(StringResolverTest)


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
