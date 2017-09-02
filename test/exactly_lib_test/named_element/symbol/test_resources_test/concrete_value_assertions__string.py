import unittest

from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.named_element.symbol.restrictions.value_restrictions import AnySymbolTypeRestriction
from exactly_lib.named_element.symbol.string_resolver import ConstantStringFragmentResolver, \
    SymbolStringFragmentResolver, \
    StringResolver, string_constant
from exactly_lib.type_system.data.concrete_string_values import ConstantFragment
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.named_element.symbol.test_resources import concrete_value_assertions as sut
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
            (ConstantStringFragmentResolver('abc'),
             ConstantStringFragmentResolver('abc')),
            (SymbolStringFragmentResolver(
                NamedElementReference('symbol_name',
                                      ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction()))),
             SymbolStringFragmentResolver(
                 NamedElementReference('symbol_name',
                                       ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction())))),
        ]
        for fragment1, fragment2 in test_cases:
            with self.subTest(msg=str(fragment1) + ' ' + str(fragment2)):
                sut.equals_string_fragment(fragment1).apply_without_message(self, fragment2)
                sut.equals_string_fragment(fragment2).apply_without_message(self, fragment1)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        value = 'a_value'
        string_fragment = ConstantStringFragmentResolver(value)
        symbol_fragment = SymbolStringFragmentResolver(
            NamedElementReference(value, ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction())))
        assertion = sut.equals_string_fragment(string_fragment)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, symbol_fragment)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        value = 'a_value'
        string_fragment = ConstantStringFragmentResolver(value)
        symbol_fragment = SymbolStringFragmentResolver(
            NamedElementReference(value, ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction())))
        assertion = sut.equals_string_fragment(symbol_fragment)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, string_fragment)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        fragment1 = ConstantStringFragmentResolver('value 1')
        fragment2 = ConstantStringFragmentResolver('value 2')
        assertion = sut.equals_string_fragment(fragment1)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, fragment2)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        fragment1 = SymbolStringFragmentResolver(NamedElementReference('symbol_name_1',
                                                                       ReferenceRestrictionsOnDirectAndIndirect(
                                                                           AnySymbolTypeRestriction())))
        fragment2 = SymbolStringFragmentResolver(NamedElementReference('symbol_name_2',
                                                                       ReferenceRestrictionsOnDirectAndIndirect(
                                                                           AnySymbolTypeRestriction())))
        assertion = sut.equals_string_fragment(fragment1)
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
                (ConstantStringFragmentResolver('abc'),),
                (ConstantStringFragmentResolver('abc'),),
            ),
            (
                (SymbolStringFragmentResolver(NamedElementReference('symbol_name',
                                                                    ReferenceRestrictionsOnDirectAndIndirect(
                                                                        AnySymbolTypeRestriction()))),),
                (SymbolStringFragmentResolver(NamedElementReference('symbol_name',
                                                                    ReferenceRestrictionsOnDirectAndIndirect(
                                                                        AnySymbolTypeRestriction()))),),
            ),
            (
                (ConstantStringFragmentResolver('abc'),
                 SymbolStringFragmentResolver(NamedElementReference('symbol_name',
                                                                    ReferenceRestrictionsOnDirectAndIndirect(
                                                                        AnySymbolTypeRestriction()))),),
                (ConstantStringFragmentResolver('abc'),
                 SymbolStringFragmentResolver(NamedElementReference('symbol_name',
                                                                    ReferenceRestrictionsOnDirectAndIndirect(
                                                                        AnySymbolTypeRestriction()))),),
            ),
        ]
        for fragments1, fragments2 in test_cases:
            with self.subTest(msg=str(fragments1) + ' ' + str(fragments2)):
                sut.equals_string_fragments(fragments1).apply_without_message(self, fragments2)
                sut.equals_string_fragments(fragments2).apply_without_message(self, fragments1)

    def test_not_equals__different_number_of_fragments__empty__non_empty(self):
        # ARRANGE #
        expected = ()
        actual = (ConstantStringFragmentResolver('value'),)
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__different_number_of_fragments__non_empty__empty(self):
        # ARRANGE #
        expected = (ConstantStringFragmentResolver('value'),)
        actual = ()
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__same_length__different_values(self):
        # ARRANGE #
        expected = (ConstantStringFragmentResolver('expected value'),)
        actual = (ConstantStringFragmentResolver('actual value'),)
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__same_length__different_types(self):
        # ARRANGE #
        expected = (ConstantStringFragmentResolver('value'),)
        actual = (SymbolStringFragmentResolver(NamedElementReference('value',
                                                                     ReferenceRestrictionsOnDirectAndIndirect(
                                                                         AnySymbolTypeRestriction()))),)
        assertion = sut.equals_string_fragments(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class TestEquals(unittest.TestCase):
    def test_with_and_without_references(self):
        test_cases = [
            ('Plain string',
             string_constant('string value'),
             empty_symbol_table(),
             ),
            ('String with reference',
             resolver_with_references([NamedElementReference('symbol_name',
                                                             ReferenceRestrictionsOnDirectAndIndirect(
                                                                 AnySymbolTypeRestriction()))]),
             empty_symbol_table(),
             ),
        ]
        for test_case_name, string_value, symbol_table in test_cases:
            assert isinstance(string_value, StringResolver), 'Type info for IDE'
            with self.subTest(msg='{}::with checked references::{}'.format(sut.equals_string_resolver.__name__,
                                                                           test_case_name)):
                assertion = sut.equals_string_resolver(string_value)
                assertion.apply_with_message(self, string_value, test_case_name)


class TestNotEquals3(unittest.TestCase):
    def test_differs__resolved_value(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected = string_constant(expected_string)
        actual = string_constant('actual value')
        assertion = sut.equals_string_resolver(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__number_of_references(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected = string_constant(expected_string)
        actual = resolver_with_references([NamedElementReference('symbol_name',
                                                                 ReferenceRestrictionsOnDirectAndIndirect(
                                                                     AnySymbolTypeRestriction()))])
        assertion = sut.equals_string_resolver(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__different_number_of_references(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected_references = [
            NamedElementReference('expected_symbol_name',
                                  ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction()))]
        actual_references = [
            NamedElementReference('actual_symbol_name',
                                  ReferenceRestrictionsOnDirectAndIndirect(AnySymbolTypeRestriction()))]
        expected = _StringResolverTestImpl(expected_string, expected_references)
        actual = _StringResolverTestImpl(expected_string, actual_references)
        assertion = sut.equals_string_resolver(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__different_number_of_fragments(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected_fragments = (ConstantStringFragmentResolver('value'),)
        actual_fragments = ()
        expected = _StringResolverTestImpl(expected_string, [], expected_fragments)
        actual = _StringResolverTestImpl(expected_string, [], actual_fragments)
        assertion = sut.equals_string_resolver(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__different_fragments(self):
        # ARRANGE #
        expected_string = 'expected value'
        expected_fragments = (ConstantStringFragmentResolver('value 1'),)
        actual_fragments = (ConstantStringFragmentResolver('value 2'),)
        expected = _StringResolverTestImpl(expected_string, [], expected_fragments)
        actual = _StringResolverTestImpl(expected_string, [], actual_fragments)
        assertion = sut.equals_string_resolver(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


def resolver_with_references(symbol_references: list) -> StringResolver:
    fragment_resolvers = tuple([SymbolStringFragmentResolver(sym_ref)
                                for sym_ref in symbol_references])
    return StringResolver(fragment_resolvers)


class _StringResolverTestImpl(StringResolver):
    def __init__(self,
                 value: str,
                 explicit_references: list,
                 fragment_resolvers: tuple = ()):
        super().__init__(fragment_resolvers)
        self.value = value
        self.explicit_references = explicit_references
        self._fragments = fragment_resolvers

    def resolve(self, symbols: SymbolTable) -> StringValue:
        return StringValue((ConstantFragment(self.value),))

    @property
    def references(self) -> list:
        return self.explicit_references
