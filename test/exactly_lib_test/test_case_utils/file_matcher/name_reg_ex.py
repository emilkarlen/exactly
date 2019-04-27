import pathlib
import re
import unittest

from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_utils import container, symbol_table_from_name_and_resolvers
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matcher_models as model
from exactly_lib_test.test_case_utils.file_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ArrangementPostAct
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
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
        TestWithSymbolReferences(),
        ValidationShouldFailWhenRegexIsInvalid(),
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
                matcher = FileMatcherBaseNameRegExPattern(re.compile(reg_ex_pattern))
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
                        model=
                        ARBITRARY_MODEL,
                        arrangement=
                        ArrangementPostAct(
                            symbols=symbol_table_from_name_and_resolvers(regex_case.symbols)
                        ),
                        expectation=
                        expectation(
                            symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                            validation=regex_case.expectation
                        )
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
