import unittest

from exactly_lib.test_case_utils.file_matcher.sdvs import file_matcher_constant_sdv
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer, SequenceStringTransformer
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.string_transformer import StringTransformerSdvConstantTestImpl
from exactly_lib_test.test_case_utils.string_transformers.test_resources import sdv_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestResolvedValueMatchesStringTransformer)


class TestResolvedValueMatchesStringTransformer(unittest.TestCase):
    def test_matches_string_transformer(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_STRING_TRANSFORMER_SDV),
                         )),

        ]
        actual_and_expected = IdentityStringTransformer()
        sdv = StringTransformerSdvConstant(actual_and_expected)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_matches_string_transformer(
                    value=asrt.anything_goes(),
                    symbols=case.value,
                )
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, sdv)

    def test_SHOULD_not_match_WHEN_actual_is_file_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_STRING_TRANSFORMER_SDV),
                         )),

        ]
        actual = FileMatcherTestImpl()

        sdv_of_actual = file_matcher_constant_sdv(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_matches_string_transformer(
                    asrt.anything_goes(),
                    symbols=case.value
                )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, sdv_of_actual)

    def test_SHOULD_not_match_WHEN_actual_is_different_string_transformer(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_STRING_TRANSFORMER_SDV),
                         )),

        ]
        actual = SequenceStringTransformer([])

        sdv_of_actual = StringTransformerSdvConstant(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_matches_string_transformer(
                    value=asrt.fail('unconditional unexpected'),
                    symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, sdv_of_actual)

    def test_matches_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = StringTransformerSdvConstantTestImpl(
            IdentityStringTransformer(),
            references=actual_references)
        assertion_to_check = sut.resolved_value_matches_string_transformer(
            value=asrt.anything_goes(),
            references=asrt.matches_sequence([
                asrt.is_(actual_reference)
            ]),
        )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_sdv)

    def test_not_matches_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = StringTransformerSdvConstantTestImpl(
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
                assertion_to_check = sut.resolved_value_matches_string_transformer(
                    value=asrt.anything_goes(),
                    references=case.value,
                )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_sdv)


ARBITRARY_STRING_TRANSFORMER_SDV = StringTransformerSdvConstantTestImpl(IdentityStringTransformer(), [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
