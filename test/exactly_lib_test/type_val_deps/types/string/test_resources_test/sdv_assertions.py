import unittest
from typing import List

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import TypeCategory
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction
from exactly_lib.type_val_deps.sym_ref.restrictions import TypeCategoryRestriction
from exactly_lib.type_val_deps.types.string import string_sdvs
from exactly_lib.type_val_deps.types.string.string_sdv import StringSdv
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.type_val_deps.types.string.test_resources import sdv_assertions as sut
from exactly_lib_test.type_val_deps.types.string.test_resources.string_sdvs import StringSdvTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsFragmentWithExactType),
        unittest.makeSuite(TestEqualsFragments),
        unittest.makeSuite(TestEquals),
    ])


class TestEqualsFragmentWithExactType(unittest.TestCase):
    def test_equals(self):
        a_string = 'a string'
        an_identical_string = 'a string'
        test_cases = [
            NEA('constant strings',
                string_sdvs.str_fragment(a_string),
                string_sdvs.str_fragment(an_identical_string),
                ),
            NEA('symbol references',
                string_sdvs.symbol_fragment(
                    SymbolReference(a_string,
                                    ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))),
                string_sdvs.symbol_fragment(
                    SymbolReference(an_identical_string,
                                    ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))),
                ),
            NEA('symbol references with different restrictions (surprisingly)',
                string_sdvs.symbol_fragment(
                    SymbolReference(a_string,
                                    ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))),
                string_sdvs.symbol_fragment(
                    SymbolReference(an_identical_string,
                                    TypeCategoryRestriction(TypeCategory.LOGIC))),
                ),
        ]
        for case in test_cases:
            with self.subTest(case.name):
                sut.equals_string_fragment_sdv_with_exact_type(case.expected).apply_without_message(self, case.actual)
                sut.equals_string_fragment_sdv_with_exact_type(case.actual).apply_without_message(self, case.expected)

    def test_not_equals(self):
        # ARRANGE #
        value = 'a_value'
        cases = [
            NEA(
                'different constants',
                string_sdvs.str_fragment('some value'),
                string_sdvs.str_fragment('some other value'),
            ),
            NEA(
                'constant and reference',
                string_sdvs.str_fragment(value),
                string_sdvs.symbol_fragment(
                    SymbolReference(
                        value,
                        ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))
                ),
            ),
            NEA(
                'references with different names',
                string_sdvs.symbol_fragment(
                    SymbolReference(
                        'a name',
                        ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))
                ),
                string_sdvs.symbol_fragment(
                    SymbolReference(
                        'a different name',
                        ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))
                ),
            ),
            # NEA(
            #     'references with different restrictions',
            #     string_sdvs.symbol_fragment(
            #         SymbolReference(
            #             'common name',
            #             ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))
            #     ),
            #     string_sdvs.symbol_fragment(
            #         SymbolReference(
            #             'common name',
            #             TypeCategoryRestriction(TypeCategory.LOGIC))
            #     ),
            # ),
        ]

        # ACT & ASSERT #

        for case in cases:
            with self.subTest(case.name,
                              order='expected == actual'):
                assertion = sut.equals_string_fragment_sdv_with_exact_type(case.expected)
                assert_that_assertion_fails(assertion, case.actual)
            with self.subTest(case.name,
                              order='actual == expected'):
                assertion = sut.equals_string_fragment_sdv_with_exact_type(case.actual)
                assert_that_assertion_fails(assertion, case.expected)


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
    def test_equals(self):
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

    def test_not_equals(self):
        expected_string = 'expected value'
        cases = [
            NEA(
                'differs__resolved_value',
                string_sdvs.str_constant(expected_string),
                string_sdvs.str_constant('actual value'),
            ),
            NEA(
                'differs__number_of_references',
                string_sdvs.str_constant(expected_string),
                sdv_with_references([
                    SymbolReference('symbol_name',
                                    ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))
                ]),
            ),
            NEA(
                'different_number_of_references',
                StringSdvTestImpl(expected_string, [
                    SymbolReference('expected_symbol_name',
                                    ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))]),
                StringSdvTestImpl(expected_string, [
                    SymbolReference('actual_symbol_name',
                                    ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))]),

            ),
            NEA(
                'different_number_of_fragments',
                StringSdvTestImpl(expected_string, [], (string_sdvs.str_fragment('value'),)),
                StringSdvTestImpl(expected_string, [], (())),
            ),
            NEA(
                'different_fragments',
                StringSdvTestImpl(expected_string, [], (string_sdvs.str_fragment('value 1'),)),
                StringSdvTestImpl(expected_string, [], (string_sdvs.str_fragment('value 2'),)),
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                assertion = sut.equals_string_sdv(case.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.actual)


def sdv_with_references(symbol_references: List[SymbolReference]) -> StringSdv:
    fragment_sdvs = tuple([string_sdvs.symbol_fragment(sym_ref)
                           for sym_ref in symbol_references])
    return StringSdv(fragment_sdvs)
