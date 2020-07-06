import unittest

from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.string import lines_content
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.string_matcher.quant_over_lines.test_resources import \
    TestCaseBase, args_constructor_for
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _NoLineMatchesRegEx(),
        _ALineMatchesRegEx(),
        _AWholeLineMatchesRegEx(),
        _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(),
    ])


class _NoLineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        regex_arg_str = syntax_for_regex_matcher('123')
        self._check_variants_with_expectation_type(
            args_constructor_for(line_matcher=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.FAIL,
            quantifier=Quantifier.EXISTS,
            actual_file_contents=actual_contents,
        )


class _ALineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        regex_arg_str = syntax_for_regex_matcher('MATCH')
        self._check_variants_with_expectation_type(
            args_constructor_for(line_matcher=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            quantifier=Quantifier.EXISTS,
            actual_file_contents=actual_contents,
        )


class _AWholeLineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        regex_arg_str = syntax_for_regex_matcher('^MATCH$')
        self._check_variants_with_expectation_type(
            args_constructor_for(line_matcher=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            quantifier=Quantifier.EXISTS,
            actual_file_contents=actual_contents,
        )


class _WhenStringTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = StringTransformerSymbolContext.of_primitive(
            'the_transformer',
            string_transformers.to_uppercase()
        )

        actual_original_contents = lines_content(['only',
                                                  'lowercase',
                                                  'letters'])

        reg_ex_that_matches_uppercase_character = '[A-Z]'

        symbol_table_with_transformer = named_transformer.symbol_table

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_references = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        self._check_variants_with_expectation_type(
            args_constructor_for(
                line_matcher=syntax_for_regex_matcher(reg_ex_that_matches_uppercase_character),
                transformer=named_transformer.name),
            expected_result_of_positive_test=PassOrFail.PASS,
            quantifier=Quantifier.EXISTS,
            actual_file_contents=actual_original_contents,
            symbols=symbol_table_with_transformer,
            expected_symbol_references=expected_symbol_references,
        )
