import unittest

from typing import Sequence

from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.string_matcher.string_matchers import StringMatcherConstant
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherResolverConstantTestImpl
from exactly_lib_test.test_case_utils.string_matcher.test_resources import assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesStringMatcherResolver)


class TestMatchesStringMatcherResolver(unittest.TestCase):
    def test_SHOULD_match_WHEN_whole_structure_is_valid(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_RESOLVER),
                         )),

        ]
        resolver = ARBITRARY_RESOLVER
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_resolver(symbols=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, resolver)

    def test_SHOULD_not_match_WHEN_actual_is_file_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_RESOLVER),
                         )),

        ]
        resolver_of_actual = FileMatcherConstantResolver(FileMatcherTestImpl())

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_resolver(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, resolver_of_actual)

    def test_SHOULD_not_match_WHEN_validator_is_none(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_RESOLVER),
                         )),

        ]
        resolver_of_actual = StringMatcherResolverConstantTestImpl(StringMatcherConstant(None),
                                                                   validator=None)

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_resolver(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, resolver_of_actual)

    def test_SHOULD_not_match_WHEN_assertion_on_matcher_fails(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_RESOLVER),
                         )),

        ]
        resolver_of_actual = ARBITRARY_RESOLVER

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_resolver(primitive_value=asrt.fail('unconditionally'),
                                                                         symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, resolver_of_actual)

    def test_SHOULD_match_WHEN_references_match(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_resolver = arbitrary_resolver_with_references(actual_references)

        assertion_to_check = sut.matches_string_matcher_resolver(references=asrt.matches_sequence([
            asrt.is_(actual_reference)
        ]),
        )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_resolver)

    def test_SHOULD_not_match_WHEN_references_do_not_match(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_resolver = arbitrary_resolver_with_references(actual_references)

        cases = [
            NameAndValue('assert no references',
                         asrt.is_empty_sequence),
            NameAndValue('assert single invalid reference',
                         asrt.matches_sequence([
                             asrt.not_(asrt.is_(actual_reference))
                         ])),
        ]

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_resolver(references=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_resolver)


ARBITRARY_RESOLVER = StringMatcherResolverConstantTestImpl(StringMatcherConstant(None),
                                                           [])


def arbitrary_resolver_with_references(references: Sequence[SymbolReference]) -> StringMatcherResolver:
    return StringMatcherResolverConstantTestImpl(StringMatcherConstant(None),
                                                 references)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
