import pathlib
import unittest

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_utils import container, symbol_table_from_name_and_sdvs
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax, integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ARBITRARY_MODEL
from exactly_lib_test.test_case_utils.file_matcher.test_resources.test_utils import Actual
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, ParseExpectation, \
    ExecutionExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.regex.test_resources.argument_syntax import reg_ex_args_list
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess, PassOrFail
from exactly_lib_test.test_resources.matcher_argument import NameRegexComponent
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestRegExPatternOnBaseName(),
        ParseShouldFailWhenRegexArgumentIsMissing(),
        TestWithSymbolReferences(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


def name_matches_regex_arg(regex: str) -> arg.FileMatcherArg:
    return arg.Name(arg.NameRegexVariant(NameRegexComponent(regex)))


class TestRegExPatternOnBaseName(test_case_utils.TestCaseBase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NEA('match basename with exact match',
                True,
                Actual(
                    Arguments(argument_syntax.base_name_reg_ex_pattern_matcher_of(
                        reg_ex_args_list('.*name'),
                    )),
                    pathlib.Path('file name'),
                ),
                ),
            NEA('match basename with substring match',
                True,
                Actual(
                    Arguments(argument_syntax.base_name_reg_ex_pattern_matcher_of(
                        reg_ex_args_list('PA..ERN')
                    )),
                    pathlib.Path('before PATTERN after'),
                ),
                ),
            NEA('match name with pattern that matches path components',
                False,
                Actual(
                    Arguments(argument_syntax.base_name_reg_ex_pattern_matcher_of(
                        reg_ex_args_list('dir-name')
                    )),
                    pathlib.Path('dir-name') / pathlib.Path('base-name'),
                ),
                ),
            NEA('not match, because pattern is not in path',
                False,
                Actual(
                    Arguments(argument_syntax.base_name_reg_ex_pattern_matcher_of(
                        reg_ex_args_list('PATTERN')
                    )),
                    pathlib.Path('not the pattern'),
                ),
                ),
            NEA('not match, because pattern with unexpected case is in base name',
                False,
                Actual(
                    Arguments(argument_syntax.base_name_reg_ex_pattern_matcher_of(
                        reg_ex_args_list('base name')
                    )),
                    pathlib.Path('THE BASE NAME'),
                ),
                ),
            NEA('match, because pattern with unexpected case is in base name, but test is case insensitive',
                True,
                Actual(
                    Arguments(argument_syntax.base_name_reg_ex_pattern_matcher_of(
                        reg_ex_args_list('base name',
                                         ignore_case=True)
                    )),
                    pathlib.Path('THE BASE NAME'),
                ),
                ),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)


class ParseShouldFailWhenRegexArgumentIsMissing(test_case_utils.TestWithNegationArgumentBase):
    argument_w_opt_neg = arg.WithOptionalNegation(
        arg.Custom('')
    )

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._assert_failing_parse(
            remaining_source(str(self.argument_w_opt_neg.get(maybe_not.expectation_type)))
        )


class ValidationShouldFailWhenRegexIsInvalid(test_case_utils.TestCaseBase):
    def runTest(self):
        for regex_case in failing_regex_validation_cases():
            argument_w_opt_neg = arg.WithOptionalNegation(
                name_matches_regex_arg(regex_case.regex_string)
            )
            for expectation_type in ExpectationType:
                with self.subTest(expectation_type=expectation_type,
                                  validation_case=regex_case.case_name):
                    self._check_with_source_variants(
                        arguments=
                        Arguments(str(argument_w_opt_neg.get(expectation_type))),
                        model_constructor=
                        ARBITRARY_MODEL,
                        arrangement=
                        arrangement_w_tcds(
                            symbols=symbol_table_from_name_and_sdvs(regex_case.symbols)
                        ),
                        expectation=
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                            ),
                            ExecutionExpectation(
                                validation=regex_case.expectation
                            ),
                        )
                    )


class TestWithSymbolReferences(test_case_utils.TestWithNegationArgumentBase):
    any_char_regex_string_symbol = NameAndValue(
        'valid_regex_string_symbol',
        container(string_sdvs.str_constant('.'))
    )
    argument_w_opt_neg = arg.WithOptionalNegation(
        name_matches_regex_arg('AB' + symbol_reference_syntax_for_name(any_char_regex_string_symbol.name))
    )
    arrangement = arrangement_w_tcds(
        symbols=SymbolTable({
            any_char_regex_string_symbol.name: any_char_regex_string_symbol.value,
        }))

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._check_with_source_variants(
            arguments=
            Arguments(str(self.argument_w_opt_neg.get(maybe_not.expectation_type))),
            model_constructor=
            integration_check.constant_relative_file_name('ABC'),
            arrangement=self.arrangement,
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_valid_regex_string_part(self.any_char_regex_string_symbol.name),
                    ]),
                ),
                ExecutionExpectation(
                    main_result=maybe_not.main_result(PassOrFail.PASS)
                ),
            )
        )
