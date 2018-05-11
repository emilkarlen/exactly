import unittest

from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer, SequenceStringTransformer
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.lines_transformer import StringTransformerResolverConstantTestImpl
from exactly_lib_test.test_case_utils.string_transformers.test_resources import resolver_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestResolvedValueEqualsLinesTransformer),
    ])


class TestResolvedValueEqualsLinesTransformer(unittest.TestCase):
    def test_equals_lines_transformer(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_LINE_TRANSFORMER_RESOLVER),
                         )),

        ]
        actual_and_expected = IdentityStringTransformer()
        resolver = StringTransformerConstant(actual_and_expected)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_lines_transformer(actual_and_expected,
                                                                                 symbols=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, resolver)

    def test_SHOULD_not_equal_lines_transformer_WHEN_actual_is_file_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_LINE_TRANSFORMER_RESOLVER),
                         )),

        ]
        actual = FileMatcherTestImpl()
        expected = IdentityStringTransformer()

        resolver_of_actual = FileMatcherConstantResolver(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_lines_transformer(expected,
                                                                                        symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_SHOULD_not_equal_lines_transformer_WHEN_actual_is_different_lines_transformer(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_LINE_TRANSFORMER_RESOLVER),
                         )),

        ]
        actual = SequenceStringTransformer([])
        expected = IdentityStringTransformer()

        resolver_of_actual = StringTransformerConstant(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_lines_transformer(expected,
                                                                                        symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_resolver = StringTransformerResolverConstantTestImpl(
            IdentityStringTransformer(),
            references=actual_references)
        assertion_to_check = sut.resolved_value_equals_lines_transformer(actual_resolver.resolved_value,
                                                                         references=asrt.matches_sequence([
                                                                             asrt.is_(actual_reference)
                                                                         ]),
                                                                         )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_resolver)

    def test_not_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_resolver = StringTransformerResolverConstantTestImpl(
            IdentityStringTransformer(),
            references=actual_references)

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
                assertion_to_check = sut.resolved_value_equals_lines_transformer(actual_resolver.resolved_value,
                                                                                 references=case.value,
                                                                                 )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_resolver)


ARBITRARY_LINE_TRANSFORMER_RESOLVER = StringTransformerResolverConstantTestImpl(IdentityStringTransformer(), [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
