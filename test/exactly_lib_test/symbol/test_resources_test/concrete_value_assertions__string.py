import unittest

from exactly_lib.symbol.restrictions.concrete_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.restrictions.value_restrictions import NoRestriction
from exactly_lib.symbol.string_resolver import ConstantStringFragmentResolver, SymbolStringFragmentResolver, \
    StringResolver, string_constant
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system_values.concrete_string_values import ConstantFragment
from exactly_lib.type_system_values.string_value import StringValue
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.symbol.test_resources import concrete_value_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


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
                SymbolReference('symbol_name', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))),
             SymbolStringFragmentResolver(
                 SymbolReference('symbol_name', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction())))),
        ]
        for fragment1, fragment2 in test_cases:
            with self.subTest(msg=str(fragment1) + ' ' + str(fragment2)):
                sut.equals_string_fragment(fragment1).apply_without_message(self, fragment2)
                sut.equals_string_fragment(fragment2).apply_without_message(self, fragment1)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        value = 'a_value'
        string_fragment = ConstantStringFragmentResolver(value)
        symbol_fragment = SymbolStringFragmentResolver(
            SymbolReference(value, ReferenceRestrictionsOnDirectAndIndirect(NoRestriction())))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(string_fragment)
            assertion.apply_without_message(put, symbol_fragment)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        value = 'a_value'
        string_fragment = ConstantStringFragmentResolver(value)
        symbol_fragment = SymbolStringFragmentResolver(
            SymbolReference(value, ReferenceRestrictionsOnDirectAndIndirect(NoRestriction())))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(symbol_fragment)
            assertion.apply_without_message(put, string_fragment)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        fragment1 = ConstantStringFragmentResolver('value 1')
        fragment2 = ConstantStringFragmentResolver('value 2')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(fragment1)
            assertion.apply_without_message(put, fragment2)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        fragment1 = SymbolStringFragmentResolver(SymbolReference('symbol_name_1',
                                                                 ReferenceRestrictionsOnDirectAndIndirect(
                                                                     NoRestriction())))
        fragment2 = SymbolStringFragmentResolver(SymbolReference('symbol_name_2',
                                                                 ReferenceRestrictionsOnDirectAndIndirect(
                                                                     NoRestriction())))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(fragment1)
            assertion.apply_without_message(put, fragment2)


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
                (SymbolStringFragmentResolver(SymbolReference('symbol_name',
                                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                                  NoRestriction()))),),
                (SymbolStringFragmentResolver(SymbolReference('symbol_name',
                                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                                  NoRestriction()))),),
            ),
            (
                (ConstantStringFragmentResolver('abc'),
                 SymbolStringFragmentResolver(SymbolReference('symbol_name',
                                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                                  NoRestriction()))),),
                (ConstantStringFragmentResolver('abc'),
                 SymbolStringFragmentResolver(SymbolReference('symbol_name',
                                                              ReferenceRestrictionsOnDirectAndIndirect(
                                                                  NoRestriction()))),),
            ),
        ]
        for fragments1, fragments2 in test_cases:
            with self.subTest(msg=str(fragments1) + ' ' + str(fragments2)):
                sut.equals_string_fragments(fragments1).apply_without_message(self, fragments2)
                sut.equals_string_fragments(fragments2).apply_without_message(self, fragments1)

    def test_not_equals__different_number_of_fragments__empty__non_empty(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = ()
        actual = (ConstantStringFragmentResolver('value'),)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)

    def test_not_equals__different_number_of_fragments__non_empty__empty(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = (ConstantStringFragmentResolver('value'),)
        actual = ()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)

    def test_not_equals__same_length__different_values(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = (ConstantStringFragmentResolver('expected value'),)
        actual = (ConstantStringFragmentResolver('actual value'),)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)

    def test_not_equals__same_length__different_types(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = (ConstantStringFragmentResolver('value'),)
        actual = (SymbolStringFragmentResolver(SymbolReference('value',
                                                               ReferenceRestrictionsOnDirectAndIndirect(
                                                                   NoRestriction()))),)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)


class TestEquals(unittest.TestCase):
    def test_with_and_without_references(self):
        test_cases = [
            ('Plain string',
             string_constant('string value'),
             empty_symbol_table(),
             ),
            ('String with reference',
             resolver_with_references([SymbolReference('symbol_name',
                                                       ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))]),
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
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected = string_constant(expected_string)
        actual = string_constant('actual value')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected = string_constant(expected_string)
        actual = resolver_with_references([SymbolReference('symbol_name',
                                                           ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_references = [
            SymbolReference('expected_symbol_name', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))]
        actual_references = [
            SymbolReference('actual_symbol_name', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))]
        expected = _StringResolverTestImpl(expected_string, expected_references)
        actual = _StringResolverTestImpl(expected_string, actual_references)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_number_of_fragments(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_fragments = (ConstantStringFragmentResolver('value'),)
        actual_fragments = ()
        expected = _StringResolverTestImpl(expected_string, [], expected_fragments)
        actual = _StringResolverTestImpl(expected_string, [], actual_fragments)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_fragments(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_fragments = (ConstantStringFragmentResolver('value 1'),)
        actual_fragments = (ConstantStringFragmentResolver('value 2'),)
        expected = _StringResolverTestImpl(expected_string, [], expected_fragments)
        actual = _StringResolverTestImpl(expected_string, [], actual_fragments)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver(expected)
            assertion.apply_without_message(put, actual)


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
