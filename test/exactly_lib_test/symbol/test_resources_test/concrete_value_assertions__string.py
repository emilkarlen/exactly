import unittest

from exactly_lib.symbol.concrete_restrictions import NoRestriction
from exactly_lib.symbol.string_resolver import StringConstantFragmentResolver, StringSymbolFragmentResolver, \
    StringResolver
from exactly_lib.symbol.value_resolvers.string_resolvers import StringConstant
from exactly_lib.symbol.value_structure import SymbolReference
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
            (StringConstantFragmentResolver('abc'),
             StringConstantFragmentResolver('abc')),
            (StringSymbolFragmentResolver('symbol_name'),
             StringSymbolFragmentResolver('symbol_name')),
        ]
        for fragment1, fragment2 in test_cases:
            with self.subTest(msg=str(fragment1) + ' ' + str(fragment2)):
                sut.equals_string_fragment(fragment1).apply_without_message(self, fragment2)
                sut.equals_string_fragment(fragment2).apply_without_message(self, fragment1)

    def test_string_not_equals_symbol_ref(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        value = 'a_value'
        string_fragment = StringConstantFragmentResolver(value)
        symbol_fragment = StringSymbolFragmentResolver(value)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(string_fragment)
            assertion.apply_without_message(put, symbol_fragment)

    def test_symbol_ref_not_equals_string(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        value = 'a_value'
        string_fragment = StringConstantFragmentResolver(value)
        symbol_fragment = StringSymbolFragmentResolver(value)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(symbol_fragment)
            assertion.apply_without_message(put, string_fragment)

    def test_string_not_equals_string_with_different_value(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        fragment1 = StringConstantFragmentResolver('value 1')
        fragment2 = StringConstantFragmentResolver('value 2')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragment(fragment1)
            assertion.apply_without_message(put, fragment2)

    def test_symbol_ref_not_equals_symbol_ref_with_different_symbol_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        fragment1 = StringSymbolFragmentResolver('symbol_name_1')
        fragment2 = StringSymbolFragmentResolver('symbol_name_2')
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
                (StringConstantFragmentResolver('abc'),),
                (StringConstantFragmentResolver('abc'),),
            ),
            (
                (StringSymbolFragmentResolver('symbol_name'),),
                (StringSymbolFragmentResolver('symbol_name'),),
            ),
            (
                (StringConstantFragmentResolver('abc'),
                 StringSymbolFragmentResolver('symbol_name'),),
                (StringConstantFragmentResolver('abc'),
                 StringSymbolFragmentResolver('symbol_name'),),
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
        actual = (StringConstantFragmentResolver('value'),)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)

    def test_not_equals__different_number_of_fragments__non_empty__empty(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = (StringConstantFragmentResolver('value'),)
        actual = ()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)

    def test_not_equals__same_length__different_values(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = (StringConstantFragmentResolver('expected value'),)
        actual = (StringConstantFragmentResolver('actual value'),)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)

    def test_not_equals__same_length__different_types(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = (StringConstantFragmentResolver('value'),)
        actual = (StringSymbolFragmentResolver('value'),)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_fragments(expected)
            assertion.apply_without_message(put, actual)


class TestEquals(unittest.TestCase):
    def test_with_ignored_reference_checks(self):
        test_cases = [
            ('Plain string',
             StringConstant('string value'),
             empty_symbol_table(),
             ),
            ('String with reference',
             _StringResolverTestImpl('string value', [SymbolReference('symbol_name', NoRestriction())]),
             empty_symbol_table(),
             ),
        ]
        for test_case_name, string_value, symbol_table in test_cases:
            assert isinstance(string_value, StringResolver), 'Type info for IDE'
            with self.subTest(msg='equals_string_value2::with checked references::' + test_case_name):
                assertion = sut.equals_string_resolver3(string_value)
                assertion.apply_with_message(self, string_value, test_case_name)


class TestNotEquals3(unittest.TestCase):
    def test_differs__resolved_value(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected = StringConstant(expected_string)
        actual = StringConstant('actual value')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver3(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected = StringConstant(expected_string)
        actual = _StringResolverTestImpl(expected_string,
                                         [SymbolReference('symbol_name', NoRestriction())])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver3(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_number_of_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_references = [SymbolReference('expected_symbol_name', NoRestriction())]
        actual_references = [SymbolReference('actual_symbol_name', NoRestriction())]
        expected = _StringResolverTestImpl(expected_string, expected_references)
        actual = _StringResolverTestImpl(expected_string, actual_references)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver3(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_number_of_fragments(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_fragments = (StringConstantFragmentResolver('value'),)
        actual_fragments = ()
        expected = _StringResolverTestImpl(expected_string, [], expected_fragments)
        actual = _StringResolverTestImpl(expected_string, [], actual_fragments)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver3(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__different_fragments(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected_string = 'expected value'
        expected_fragments = (StringConstantFragmentResolver('value 1'),)
        actual_fragments = (StringConstantFragmentResolver('value 2'),)
        expected = _StringResolverTestImpl(expected_string, [], expected_fragments)
        actual = _StringResolverTestImpl(expected_string, [], actual_fragments)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_string_resolver3(expected)
            assertion.apply_without_message(put, actual)


class _StringResolverTestImpl(StringResolver):
    def __init__(self,
                 value: str,
                 explicit_references: list,
                 fragments: tuple() = ()):
        self.value = value
        self.explicit_references = explicit_references
        self._fragments = fragments

    def resolve(self, symbols: SymbolTable) -> str:
        return self.value

    @property
    def fragments(self) -> tuple:
        return self._fragments

    @property
    def references(self) -> list:
        return self.explicit_references
