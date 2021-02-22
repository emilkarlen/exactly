import unittest
from typing import List

from exactly_lib.type_val_prims.matcher import line_matcher
from exactly_lib.util.str_.formatter import StringFormatter
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.impls.types.line_matcher.test_resources import validation_cases, line_matchers
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ExecutionExpectation, arrangement_wo_tcds, \
    MultiSourceExpectation
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.regex.test_resources import assertions as asrt_regex
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformer.replace.test_resources import \
    expectation_of_successful_replace_execution__multi
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformer.test_resources.abstract_syntaxes import ReplaceRegexAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_val_deps.test_resources.data import data_restrictions_assertions as asrt_ref_rest
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.line_matcher import LineMatcherSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ValidatorShouldValidateLineMatcher(),
        unittest.makeSuite(TestApplication),
    ])


class ValidatorShouldValidateLineMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for validation_case in validation_cases.failing_validation_cases():
            for preserve_new_lines in [False, True]:
                syntax = ReplaceRegexAbsStx.of_str('valid_regex',
                                                   'valid_replacement',
                                                   preserve_new_lines=preserve_new_lines,
                                                   lines_filter=validation_case.value.matcher_abs_stx,
                                                   )

                line_matcher_symbol_context = validation_case.value.symbol_context
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__abs_stx__layout__std_source_variants(
                    self,
                    syntax,
                    model_constructor.arbitrary(self),
                    arrangement_wo_tcds(
                        symbols=line_matcher_symbol_context.symbol_table
                    ),
                    MultiSourceExpectation(
                        symbol_references=line_matcher_symbol_context.references_assertion,
                        execution=ExecutionExpectation(
                            validation=validation_case.value.expectation,
                        )
                    ),
                    sub_test_identifiers={
                        'preserve_new_lines': preserve_new_lines,
                        'validation': validation_case.name,
                    }
                )


class TestApplication(unittest.TestCase):
    def test_only_lines_matching_line_matcher_SHOULD_be_replaced(self):
        # ARRANGE #
        pattern = r'PA[A-Z]*N'
        string_matching_pattern = 'PATTERN'
        string_not_matching_pattern = '<not matched by pattern>'
        string_matched_by_line_selector = '<MATCHED BY LINE MATCHER>'
        string_not_matched_by_line_selector = '<not matched by line matcher>'
        replacement_str = 'REPLACEMENT'
        sf = StringFormatter({
            'matches_pattern': string_matching_pattern,
            'replacement_str': replacement_str,
            'not_pattern': string_not_matching_pattern,
            'lm_match': string_matched_by_line_selector,
            'lm_no_match': string_not_matched_by_line_selector,
        })
        input_lines__tmpl = [
            '{matches_pattern} {lm_no_match}',
            '{matches_pattern} {lm_match}',
            '{not_pattern} {lm_no_match}',
            '{not_pattern} {lm_match}',
        ]
        output_lines__tmpl = [
            '{matches_pattern} {lm_no_match}',
            '{replacement_str} {lm_match}',
            '{not_pattern} {lm_no_match}',
            '{not_pattern} {lm_match}',
        ]
        input_lines = [
            sf.format(line)
            for line in input_lines__tmpl
        ]

        output_lines = [
            sf.format(line)
            for line in output_lines__tmpl
        ]

        lines_selector = LineMatcherSymbolContext.of_primitive(
            'LINES_SELECTOR_MATCHER',
            line_matchers.LineMatcherThatMatchesContentsSubString(string_matched_by_line_selector),
        )
        # ACT & ASSERT #
        self._check(
            pattern,
            replacement_str,
            lines_selector,
            input_lines,
            output_lines,
        )

    def test_line_numbering(self):
        # ARRANGE #
        matching_line_numbers = frozenset([line_matcher.FIRST_LINE_NUMBER,
                                           line_matcher.FIRST_LINE_NUMBER + 2])
        pattern = r'PA[A-Z]*N'
        string_matching_pattern = 'PATTERN'
        replacement_str = 'REPLACEMENT'
        input_lines = [
            string_matching_pattern,
            string_matching_pattern,
            string_matching_pattern,
            string_matching_pattern,
        ]
        output_lines = [
            replacement_str,  # FIRST_LINE_NUMBER
            string_matching_pattern,
            replacement_str,  # FIRST_LINE_NUMBER + 2
            string_matching_pattern,
        ]

        lines_selector = LineMatcherSymbolContext.of_primitive(
            'LINES_SELECTOR_MATCHER',
            line_matchers.LineMatcherThatMatchesLineNumbers(matching_line_numbers),
        )
        # ACT & ASSERT #
        self._check(
            pattern,
            replacement_str,
            lines_selector,
            input_lines,
            output_lines,
        )

    def _check(self,
               pattern: str,
               replacement_str: str,
               lines_selector: LineMatcherSymbolContext,
               input_lines__wo_nl: List[str],
               output_lines__wo_nl: List[str],
               ):
        # ARRANGE #
        input_lines = with_appended_new_lines(input_lines__wo_nl)
        output_lines = with_appended_new_lines(output_lines__wo_nl)

        pattern_symbol = StringConstantSymbolContext(
            'PATTERN_SYMBOL',
            pattern,
            default_restrictions=asrt_regex.is_reference_restrictions__regex(),
        )
        replacement_symbol = StringConstantSymbolContext(
            'REPLACEMENT_SYMBOL',
            replacement_str,
            default_restrictions=asrt_ref_rest.is_reference_restrictions__convertible_to_string(),
        )

        all_symbol = [lines_selector, pattern_symbol, replacement_symbol]

        for preserve_new_lines in [False, True]:
            syntax = ReplaceRegexAbsStx(
                pattern_symbol.abstract_syntax,
                replacement_symbol.abstract_syntax,
                preserve_new_lines=preserve_new_lines,
                lines_filter=lines_selector.abstract_syntax,
            )
            # ACT & ASSERT #
            integration_check.CHECKER__PARSE_FULL.check__abs_stx__layout__std_source_variants(
                self,
                syntax,
                model_constructor.of_lines(self, input_lines),
                arrangement_w_tcds(
                    symbols=SymbolContext.symbol_table_of_contexts(all_symbol),
                ),
                expectation_of_successful_replace_execution__multi(
                    symbol_references=SymbolContext.references_assertion_of_contexts(all_symbol),
                    output_lines=output_lines,
                    may_depend_on_external_resources=True,
                ),
                sub_test_identifiers={
                    'preserve_new_lines': preserve_new_lines,
                }
            )
