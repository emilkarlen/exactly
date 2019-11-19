import re
import unittest
from typing import Sequence, Pattern

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_value_validation import ConstantPreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.sdvs import FileMatcherConstantSdv
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.regex.test_resources import assertions as sut
from exactly_lib_test.test_case_utils.regex.test_resources.regex_ddvs import RegexSdvConstantTestImpl
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_case_utils.test_resources.validation import pre_sds_validation_fails, \
    post_sds_validation_fails
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.values import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesRegexResolver)


class TestMatchesRegexResolver(unittest.TestCase):
    def test_SHOULD_match_WHEN_whole_structure_is_valid(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(CONSTANT_STRING_SDV),
                         )),

        ]
        sdv = ARBITRARY_SDV
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_regex_sdv(symbols=case.value)
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
                             symbol_utils.container(CONSTANT_STRING_SDV),
                         )),

        ]
        sdv_of_actual = FileMatcherConstantSdv(FileMatcherTestImpl())

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_regex_sdv(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_validator_SHOULD_not_be_none(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(CONSTANT_STRING_SDV),
                         )),

        ]
        sdv_of_actual = RegexSdvConstantTestImpl(ARBITRARY_PATTERN,
                                                 value_validator=None)

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_regex_sdv(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_not_match_WHEN_resolved_primitive_value_is_none(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(CONSTANT_STRING_SDV),
                         )),

        ]
        sdv_of_actual = RegexSdvConstantTestImpl(None)

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_regex_sdv(symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_not_match_WHEN_resolved_primitive_value_is_not_a_pattern(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(CONSTANT_STRING_SDV),
                         )),

        ]
        sdv_of_actual = RegexSdvConstantTestImpl('not a pattern')

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_regex_sdv(symbols=case.value)
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
                             symbol_utils.container(CONSTANT_STRING_SDV),
                         )),

        ]
        sdv_of_actual = ARBITRARY_SDV

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.matches_regex_sdv(
                    primitive_value=lambda tcds: asrt.fail('unconditionally'),
                    symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_match_WHEN_references_match(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = arbitrary_sdv_with_references(actual_references)

        assertion_to_check = sut.matches_regex_sdv(
            references=asrt.matches_sequence([
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
                assertion_to_check = sut.matches_regex_sdv(references=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_sdv)

    def test_SHOULD_match_WHEN_resolving_dependencies_do_match(self):
        # ARRANGE #
        expected_dependencies = {DirectoryStructurePartition.HDS}
        actual_dependencies = expected_dependencies

        sdv_of_actual = RegexSdvConstantTestImpl(
            ARBITRARY_PATTERN,
            resolving_dependencies=actual_dependencies
        )

        assertion_to_check = sut.matches_regex_sdv(dir_dependencies=DirDependencies.HDS)

        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, sdv_of_actual)

    def test_SHOULD_not_match_WHEN_resolving_dependencies_do_not_match(self):
        # ARRANGE #
        actual_dependencies = {DirectoryStructurePartition.NON_HDS}

        sdv_of_actual = RegexSdvConstantTestImpl(
            ARBITRARY_PATTERN,
            resolving_dependencies=actual_dependencies
        )

        assertion_to_check = sut.matches_regex_sdv(dir_dependencies=DirDependencies.HDS)

        # ACT & ASSERT #
        assert_that_assertion_fails(assertion_to_check, sdv_of_actual)

    def test_SHOULD_match_WHEN_pre_sds_validation_fails_expectedly_but_primitive_value_is_unexpected(self):
        # ARRANGE #

        sdv_of_actual = RegexSdvConstantTestImpl(
            ARBITRARY_PATTERN,
            value_validator=ConstantPreOrPostSdsValueValidator(
                pre_sds_result=asrt_validation.new_single_string_text_for_test('expected failure')
            ),
        )

        assertion_to_check = sut.matches_regex_sdv(
            dir_dependencies=DirDependencies.NONE,
            validation=pre_sds_validation_fails(),
            primitive_value=check_of_primitive_value_fails_expectedly,
        )

        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, sdv_of_actual)

    def test_SHOULD_match_WHEN_post_sds_validation_fails_expectedly_but_primitive_value_is_unexpected(self):
        # ARRANGE #

        sdv_of_actual = RegexSdvConstantTestImpl(
            ARBITRARY_PATTERN,
            value_validator=ConstantPreOrPostSdsValueValidator(
                post_sds_result=asrt_validation.new_single_string_text_for_test('expected failure')
            ),
        )

        assertion_to_check = sut.matches_regex_sdv(
            dir_dependencies=DirDependencies.NONE,
            validation=post_sds_validation_fails(),
            primitive_value=check_of_primitive_value_fails_expectedly,
        )

        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, sdv_of_actual)


ARBITRARY_PATTERN = re.compile('.')

ARBITRARY_SDV = RegexSdvConstantTestImpl(ARBITRARY_PATTERN,
                                         [])

CONSTANT_STRING_SDV = string_sdvs.str_constant('constant string')


def arbitrary_sdv_with_references(references: Sequence[SymbolReference]) -> RegexSdv:
    return RegexSdvConstantTestImpl(ARBITRARY_PATTERN,
                                    references)


def check_of_primitive_value_fails_expectedly(tcds: Tcds) -> ValueAssertion[Pattern]:
    return asrt.fail('unconditional failure')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
