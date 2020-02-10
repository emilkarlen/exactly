import unittest

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.data.test_resources import concrete_value_assertions as sut
from exactly_lib_test.symbol.data.test_resources.string_sdvs import StringSdvTestImpl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsFragment),
        unittest.makeSuite(TestEqualsFragments),
        unittest.makeSuite(TestEquals),
        unittest.makeSuite(TestNotEquals3),
    ])


class TestEqualsFragment(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            (string_sdvs.str_fragment('abc'),
             string_sdvs.str_fragment('abc')),
            (string_sdvs.symbol_fragment(
                SymbolReference('symbol_name',
                                ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))),
             string_sdvs.symbol_fragment(
                 SymbolReference('symbol_name',
                                 ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction())))),
        ]
        for fragment1, fragment2 in test_cases:
            with self.subTest(msg=str(fragment1) + ' ' + str(fragment2)):
                sut.equals_string_fragment_sdv_with_exact_type(fragment1).apply_without_message(self, fragment2)
                sut.equals_string_fragment_sdv_with_exact_type(fragment2).apply_without_message(self, fragment1)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        value = 'a_value'
        string_fragment = string_sdvs.str_fragment(value)
        symbol_fragment = string_sdvs.symbol_fragment(
            SymbolReference(value, ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction())))
        assertion = sut.equals_string_fragment_sdv_with_exact_type(string_fragment)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, symbol_fragment)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        value = 'a_value'
        string_fragment = string_sdvs.str_fragment(value)
        symbol_fragment = string_sdvs.symbol_fragment(
            SymbolReference(value, ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction())))
        assertion = sut.equals_string_fragment_sdv_with_exact_type(symbol_fragment)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, string_fragment)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        fragment1 = string_sdvs.str_fragment('value 1')
        fragment2 = string_sdvs.str_fragment('value 2')
        assertion = sut.equals_string_fragment_sdv_with_exact_type(fragment1)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, fragment2)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        fragment1 = string_sdvs.symbol_fragment(SymbolReference('symbol_name_1',
                                                                ReferenceRestrictionsOnDirectAndIndirect(
                                                                         AnyDataTypeRestriction())))
        fragment2 = string_sdvs.symbol_fragment(SymbolReference('symbol_name_2',
                                                                ReferenceRestrictionsOnDirectAndIndirect(
                                                                         AnyDataTypeRestriction())))
        assertion = sut.equals_string_fragment_sdv_with_exact_type(fragment1)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, fragment2)


class TestEqualsFragments(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            (
                (),
                (),
            ),
            (
                (string_sdvs.str_fragment('abc'),),
                (string_sdvs.str_fragment('abc'),),
            ),
            (
                (string_sdvs.symbol_fragment(SymbolReference('symbol_name',
                                                             ReferenceRestrictionsOnDirectAndIndirect(
                                                                      AnyDataTypeRestriction()))),),
                (string_sdvs.symbol_fragment(SymbolReference('symbol_name',
                                                             ReferenceRestrictionsOnDirectAndIndirect(
                                                                      AnyDataTypeRestriction()))),),
            ),
            (
                (string_sdvs.str_fragment('abc'),
                 string_sdvs.symbol_fragment(SymbolReference('symbol_name',
                                                             ReferenceRestrictionsOnDirectAndIndirect(
                                                                      AnyDataTypeRestriction()))),),
                (string_sdvs.str_fragment('abc'),
                 string_sdvs.symbol_fragment(SymbolReference('symbol_name',
                                                             ReferenceRestrictionsOnDirectAndIndirect(
                                                                      AnyDataTypeRestriction()))),),
            ),
        ]
        for fragments1, fragments2 in test_cases:
            with self.subTest(msg=str(fragments1) + ' ' + str(fragments2)):
                sut.equals_string_fragments(fragments1).apply_without_message(self, fragments2)
                sut.equals_string_fragments(fragments2).apply_without_message(self, fragments1)

    def test_not_equals__different_number_of_fragments__empty__non_empty(self):
        # ARRANGE #
        expected = ()
        actual = (string_sdvs.str_fragment('value'),)
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__different_number_of_fragments__non_empty__empty(self):
        # ARRANGE #
        expected = (string_sdvs.str_fragment('value'),)
        actual = ()
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__same_length__different_values(self):
        # ARRANGE #
        expected = (string_sdvs.str_fragment('expected value'),)
        actual = (string_sdvs.str_fragment('actual value'),)
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__same_length__different_types(self):
        # ARRANGE #
        expected = (string_sdvs.str_fragment('value'),)
        actual = (string_sdvs.symbol_fragment(SymbolReference('value',
                                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                                       AnyDataTypeRestriction()))),)
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class TestEquals(unittest.TestCase):
    def test_with_and_without_references(self):
        test_cases = [
            ('Plain string',
             string_sdvs.str_constant('string value'),
             empty_symbol_table(),
             ),
            ('String with reference',
             sdv_with_references([SymbolReference('symbol_name',
                                                  ReferenceRestrictionsOnDirectAndIndirect(
                                                           AnyDataTypeRestriction()))]),
             empty_symbol_table(),
             ),
        ]
        for test_case_name, string_value, symbol_table in test_cases:
            assert isinstance(string_value, StringSdv), 'Type info for IDE'
            with self.subTest(msg='{}::with checked references::{}'.format(sut.equals_string_sdv.__name__,
                                                                           test_case_name)):
                assertion = sut.equals_string_sdv(string_value)
                assertion.apply_with_message(self, string_value, test_case_name)


class TestNotEquals3(unittest.TestCase):
    def test_differs__resolved_value(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected = string_sdvs.str_constant(expected_string)
        actual = string_sdvs.str_constant('actual value')
        assertion = sut.equals_string_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__number_of_references(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected = string_sdvs.str_constant(expected_string)
        actual = sdv_with_references([SymbolReference('symbol_name',
                                                      ReferenceRestrictionsOnDirectAndIndirect(
                                                               AnyDataTypeRestriction()))])
        assertion = sut.equals_string_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__different_number_of_references(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected_references = [
            SymbolReference('expected_symbol_name',
                            ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))]
        actual_references = [
            SymbolReference('actual_symbol_name',
                            ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))]
        expected = StringSdvTestImpl(expected_string, expected_references)
        actual = StringSdvTestImpl(expected_string, actual_references)
        assertion = sut.equals_string_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__different_number_of_fragments(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected_fragments = (string_sdvs.str_fragment('value'),)
        actual_fragments = ()
        expected = StringSdvTestImpl(expected_string, [], expected_fragments)
        actual = StringSdvTestImpl(expected_string, [], actual_fragments)
        assertion = sut.equals_string_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__different_fragments(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected_fragments = (string_sdvs.str_fragment('value 1'),)
        actual_fragments = (string_sdvs.str_fragment('value 2'),)
        expected = StringSdvTestImpl(expected_string, [], expected_fragments)
        actual = StringSdvTestImpl(expected_string, [], actual_fragments)
        assertion = sut.equals_string_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


def sdv_with_references(symbol_references: list) -> StringSdv:
    fragment_sdvs = tuple([string_sdvs.symbol_fragment(sym_ref)
                           for sym_ref in symbol_references])
    return StringSdv(fragment_sdvs)
