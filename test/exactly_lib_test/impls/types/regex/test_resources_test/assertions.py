import re
import unittest
from typing import Sequence, Pattern

from exactly_lib.impls.types.regex.regex_ddv import RegexSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import ConstantDdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependencies
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.type_val_deps.test_resources.validation import validation as asrt_validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.regex.test_resources import assertions as sut
from exactly_lib_test.impls.types.regex.test_resources.regex_ddvs import RegexSdvConstantTestImpl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import references as data_references
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.file_matchers import file_matcher_constant_sdv
from exactly_lib_test.type_val_deps.types.string_.test_resources import symbol_context as string
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext
from exactly_lib_test.type_val_prims.test_resources.primitives import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesRegexResolver)


class TestMatchesRegexResolver(unittest.TestCase):
    def test_SHOULD_match_WHEN_whole_structure_is_valid(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         StringSymbolContext(
                             'the symbol name',
                             string.ARBITRARY_SYMBOL_VALUE_CONTEXT).symbol_table,
                         ),

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
                         StringSymbolContext(
                             'the symbol name',
                             string.ARBITRARY_SYMBOL_VALUE_CONTEXT).symbol_table,
                         ),

        ]
        sdv_of_actual = file_matcher_constant_sdv(FileMatcherTestImpl())

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
                         StringSymbolContext.of_sdv(
                             'the symbol name',
                             CONSTANT_STRING_SDV).symbol_table,
                         ),

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
                         StringSymbolContext.of_sdv(
                             'the symbol name',
                             CONSTANT_STRING_SDV).symbol_table
                         ),

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
                         StringSymbolContext.of_sdv(
                             'the symbol name',
                             CONSTANT_STRING_SDV).symbol_table,
                         ),

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
                         StringSymbolContext.of_sdv(
                             'the symbol name',
                             CONSTANT_STRING_SDV).symbol_table,
                         ),

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
        actual_reference = data_references.reference_to__on_direct_and_indirect('referenced element')
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
        actual_reference = data_references.reference_to__on_direct_and_indirect('referenced element')
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
            value_validator=ConstantDdvValidator(
                pre_sds_result=asrt_validation.new_single_string_text_for_test('expected failure')
            ),
        )

        assertion_to_check = sut.matches_regex_sdv(
            dir_dependencies=DirDependencies.NONE,
            validation=ValidationAssertions.pre_sds_fails(),
            primitive_value=check_of_primitive_value_fails_expectedly,
        )

        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, sdv_of_actual)

    def test_SHOULD_match_WHEN_post_sds_validation_fails_expectedly_but_primitive_value_is_unexpected(self):
        # ARRANGE #

        sdv_of_actual = RegexSdvConstantTestImpl(
            ARBITRARY_PATTERN,
            value_validator=ConstantDdvValidator(
                post_sds_result=asrt_validation.new_single_string_text_for_test('expected failure')
            ),
        )

        assertion_to_check = sut.matches_regex_sdv(
            dir_dependencies=DirDependencies.NONE,
            validation=ValidationAssertions.post_sds_fails(),
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


def check_of_primitive_value_fails_expectedly(tcds: TestCaseDs) -> Assertion[Pattern]:
    return asrt.fail('unconditional failure')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
