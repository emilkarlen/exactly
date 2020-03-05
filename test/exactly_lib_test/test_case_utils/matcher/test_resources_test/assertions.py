import unittest
from typing import Sequence

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeStv
from exactly_lib.symbol.logic.string_matcher import StringMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.sdvs import file_matcher_constant_sdv
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import singleton_symbol_table_2, SymbolTable
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.string_matcher import string_matcher_sdv_constant_test_impl
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources import assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
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
                             symbol_utils.container(ARBITRARY_STRING_MATCHER_SDV),
                         )),

        ]
        sdv = ARBITRARY_STRING_MATCHER_SDV
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = _matches_string_matcher_sdv(symbols=case.value)
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
                             symbol_utils.container(ARBITRARY_STRING_MATCHER_SDV),
                         )),

        ]
        sdv_of_actual = file_matcher_constant_sdv(FileMatcherTestImpl())

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = _matches_string_matcher_sdv(symbols=case.value)
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
                             symbol_utils.container(ARBITRARY_STRING_MATCHER_SDV),
                         )),

        ]
        sdv_of_actual = string_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(True),
                                                              validator=None)

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = _matches_string_matcher_sdv(symbols=case.value)
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
                             symbol_utils.container(ARBITRARY_STRING_MATCHER_SDV),
                         )),

        ]
        sdv_of_actual = ARBITRARY_STRING_MATCHER_SDV

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = _matches_string_matcher_sdv(primitive_value=asrt.fail('unconditionally'),
                                                                 symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_match_WHEN_references_match(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = arbitrary_sdv_with_references(actual_references)

        assertion_to_check = _matches_string_matcher_sdv(references=asrt.matches_sequence([
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
                assertion_to_check = _matches_string_matcher_sdv(references=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_sdv)


ARBITRARY_STRING_MATCHER_SDV = string_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(True))


def _matches_string_matcher_sdv(primitive_value: ValueAssertion[MatcherWTraceAndNegation] = asrt.anything_goes(),
                                references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                symbols: SymbolTable = None,
                                tcds: Tcds = fake_tcds(),
                                ) -> ValueAssertion[LogicTypeStv]:
    return sut.matches_matcher_stv(StringMatcherStv, LogicValueType.STRING_MATCHER, primitive_value, references,
                                   symbols, tcds)


def arbitrary_sdv_with_references(references: Sequence[SymbolReference]) -> StringMatcherStv:
    return string_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(True),
                                                 references)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
