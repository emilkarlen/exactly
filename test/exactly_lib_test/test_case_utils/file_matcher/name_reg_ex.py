import unittest

import pathlib
import re

from exactly_lib.symbol.data import file_ref_resolvers, string_resolvers
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models as model
from exactly_lib_test.test_case_utils.file_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ArrangementPostAct
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess, PassOrFail
from exactly_lib_test.test_resources.matcher_argument import NameRegexComponent
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRegExPatternOnBaseName),
        ParseShouldFailWhenRegexArgumentIsMissing(),
        ValidationShouldFailPreSdsWhenHardCodedRegexIsInvalid(),
        ValidationShouldFailPostSdsWhenRegexWithPostSdsValueRefIsInvalid(),
        TestWithSymbolReferences(),
    ])


def name_matches_regex_arg(regex: str) -> arg.FileMatcherArg:
    return arg.Name(arg.NameRegexVariant(NameRegexComponent(regex)))


class TestRegExPatternOnBaseName(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('match basename with exact match',
                         (
                             '.*name',
                             pathlib.Path('file name'),
                             True,
                         )),
            NameAndValue('match basename with substring match',
                         (
                             'PA..ERN',
                             pathlib.Path('before PATTERN after'),
                             True,
                         )),
            NameAndValue('match name with pattern that matches path components',
                         (
                             'dir-name',
                             pathlib.Path('dir-name') / pathlib.Path('base-name'),
                             False,
                         )),
            NameAndValue('not match, because pattern is not in path',
                         (
                             'PATTERN',
                             pathlib.Path('not the pattern'),
                             False,
                         )),
        ]
        for case in cases:
            reg_ex_pattern, path, expected_result = case.value
            with self.subTest(case_name=case.name,
                              glob_pattern=reg_ex_pattern):
                matcher = sut.FileMatcherBaseNameRegExPattern(re.compile(reg_ex_pattern))
                # ACT #
                actual_reg_ex_pattern = matcher.reg_ex_pattern

                actual_result = matcher.matches(model.with_dir_space_that_must_not_be_used(path))

                # ASSERT #

                self.assertIsInstance(matcher.option_description,
                                      str,
                                      'option_description')

                self.assertEqual(reg_ex_pattern,
                                 actual_reg_ex_pattern,
                                 'reg-ex pattern')

                self.assertEqual(expected_result,
                                 actual_result,
                                 'result')


class ParseShouldFailWhenRegexArgumentIsMissing(test_case_utils.TestWithNegationArgumentBase):
    argument_w_opt_neg = arg.WithOptionalNegation(
        arg.Custom('')
    )

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._assert_failing_parse(
            remaining_source(str(self.argument_w_opt_neg.get(maybe_not.expectation_type)))
        )


class ValidationShouldFailPreSdsWhenHardCodedRegexIsInvalid(test_case_utils.TestWithNegationArgumentBase):
    argument_w_opt_neg = arg.WithOptionalNegation(
        name_matches_regex_arg('*')
    )

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check_with_source_variants(
            arguments=
            Arguments(str(self.argument_w_opt_neg.get(maybe_not.expectation_type))),
            model=
            ARBITRARY_MODEL,
            arrangement=
            ArrangementPostAct(),
            expectation=
            expectation(
                validation=validation.pre_sds_validation_fails()
            )
        )


class ValidationShouldFailPostSdsWhenRegexWithPostSdsValueRefIsInvalid(test_case_utils.TestWithNegationArgumentBase):
    post_sds_file_ref = NameAndValue(
        'post_sds_file_ref_symbol',
        container(file_ref_resolvers.of_rel_option(RelOptionType.REL_ACT))
    )
    argument_w_opt_neg = arg.WithOptionalNegation(
        name_matches_regex_arg('*' + symbol_reference_syntax_for_name(post_sds_file_ref.name))
    )

    arrangement = ArrangementPostAct(symbols=SymbolTable({
        post_sds_file_ref.name: post_sds_file_ref.value,
    }))
    expectation = expectation(
        symbol_references=asrt.matches_sequence([
            is_reference_to_valid_regex_string_part(post_sds_file_ref.name),
        ]),
        validation=validation.post_sds_validation_fails()
    )

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check_with_source_variants(
            arguments=
            Arguments(str(self.argument_w_opt_neg.get(maybe_not.expectation_type))),
            model=
            ARBITRARY_MODEL,
            arrangement=self.arrangement,
            expectation=self.expectation
        )


class TestWithSymbolReferences(test_case_utils.TestWithNegationArgumentBase):
    any_char_regex_string_symbol = NameAndValue(
        'valid_regex_string_symbol',
        container(string_resolvers.str_constant('.'))
    )
    argument_w_opt_neg = arg.WithOptionalNegation(
        name_matches_regex_arg('AB' + symbol_reference_syntax_for_name(any_char_regex_string_symbol.name))
    )
    arrangement = ArrangementPostAct(symbols=SymbolTable({
        any_char_regex_string_symbol.name: any_char_regex_string_symbol.value,
    }))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check_with_source_variants(
            arguments=
            Arguments(str(self.argument_w_opt_neg.get(maybe_not.expectation_type))),
            model=
            model_construction.constant_relative_file_name('ABC'),
            arrangement=self.arrangement,
            expectation=expectation(
                symbol_references=asrt.matches_sequence([
                    is_reference_to_valid_regex_string_part(self.any_char_regex_string_symbol.name),
                ]),
                main_result=maybe_not.main_result(PassOrFail.PASS)
            )
        )


ARBITRARY_MODEL = model_construction.constant_relative_file_name('arbitrary-file.txt')
