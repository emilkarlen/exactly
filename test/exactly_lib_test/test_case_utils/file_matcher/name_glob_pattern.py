import pathlib
import unittest

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_syntax, integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.test_case_utils.file_matcher.test_resources.test_utils import Actual
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, arrangement_w_tcds, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess, PassOrFail
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestGlobPattern),
        ParseShouldFailWhenPatternArgumentIsMissing(),
        TestWithSymbolReferences(),
    ])


class TestGlobPattern(test_case_utils.TestCaseBase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NEA('match basename with exact match',
                True,
                Actual(
                    Arguments(argument_syntax.name_glob_pattern_matcher_of('pattern')),
                    pathlib.Path('pattern'),
                )),
            NEA('match basename with substring exact match',
                True,
                Actual(
                    Arguments(argument_syntax.name_glob_pattern_matcher_of('*PATTERN*')),
                    pathlib.Path('before PATTERN after'),
                )),
            NEA('match name with pattern that matches path components',
                True,
                Actual(
                    Arguments(argument_syntax.name_glob_pattern_matcher_of('dir-name/*.txt')),
                    pathlib.Path('dir-name') / pathlib.Path('file.txt'),
                )),
            NEA('not match, because pattern is not in path',
                False,
                Actual(
                    Arguments(argument_syntax.name_glob_pattern_matcher_of('PATTERN')),
                    pathlib.Path('not the pattern'),
                )),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)


class ParseShouldFailWhenPatternArgumentIsMissing(test_case_utils.TestWithNegationArgumentBase):
    argument_w_opt_neg = arg.WithOptionalNegation(
        arg.Name(arg.NameGlobPatternVariant(''))
    )

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._assert_failing_parse(
            remaining_source(str(self.argument_w_opt_neg.get(maybe_not.expectation_type)))
        )


class TestWithSymbolReferences(test_case_utils.TestWithNegationArgumentBase):
    any_char_glob_pattern_string_symbol = NameAndValue(
        'glob_pattern_string_symbol',
        container(string_sdvs.str_constant('*'))
    )
    argument_w_opt_neg = arg.WithOptionalNegation(
        arg.Name(arg.NameGlobPatternVariant(
            'AB' + symbol_reference_syntax_for_name(any_char_glob_pattern_string_symbol.name))
        )
    )
    arrangement = arrangement_w_tcds(symbols=SymbolTable({
        any_char_glob_pattern_string_symbol.name: any_char_glob_pattern_string_symbol.value,
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
                        is_reference_to_valid_regex_string_part(self.any_char_glob_pattern_string_symbol.name),
                    ]),
                ),
                ExecutionExpectation(
                    main_result=maybe_not.main_result(PassOrFail.PASS)
                ),
            )
        )
