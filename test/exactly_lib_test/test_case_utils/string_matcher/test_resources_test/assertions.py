import unittest
from typing import Sequence

from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_matcher.sdvs import file_matcher_constant_sdv
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSdvConstantTestImpl
from exactly_lib_test.test_case_utils.string_matcher.test_resources import assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.string_matchers import StringMatcherConstant
from exactly_lib_test.type_system.logic.test_resources.values import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesStringMatcherSdv)


class TestMatchesStringMatcherSdv(unittest.TestCase):
    def test_SHOULD_match_WHEN_whole_structure_is_valid(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_SDV),
                         )),

        ]
        sdv = ARBITRARY_SDV
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_sdv(symbols=case.value)
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
                             symbol_utils.container(ARBITRARY_SDV),
                         )),

        ]
        sdv_of_actual = file_matcher_constant_sdv(FileMatcherTestImpl())

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_sdv(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_not_match_WHEN_validator_is_none(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_SDV),
                         )),

        ]
        sdv_of_actual = StringMatcherSdvConstantTestImpl(StringMatcherConstant(None),
                                                         validator=None)

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_sdv(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_not_match_WHEN_assertion_on_matcher_fails(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_SDV),
                         )),

        ]
        sdv_of_actual = ARBITRARY_SDV

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_string_matcher_sdv(primitive_value=asrt.fail('unconditionally'),
                                                                    symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_match_WHEN_references_match(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = arbitrary_sdv_with_references(actual_references)

        assertion_to_check = sut.matches_string_matcher_sdv(references=asrt.matches_sequence([
            asrt.is_(actual_reference)
        ]),
        )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_sdv)

    def test_SHOULD_not_match_WHEN_references_do_not_match(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = arbitrary_sdv_with_references(actual_references)

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
                assertion_to_check = sut.matches_string_matcher_sdv(references=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_sdv)


ARBITRARY_SDV = StringMatcherSdvConstantTestImpl(StringMatcherConstant(None),
                                                 [])


def arbitrary_sdv_with_references(references: Sequence[SymbolReference]) -> StringMatcherSdv:
    return StringMatcherSdvConstantTestImpl(StringMatcherConstant(None),
                                            references)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
