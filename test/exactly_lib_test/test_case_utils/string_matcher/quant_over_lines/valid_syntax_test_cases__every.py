import unittest

from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.string_matcher.quant_over_lines.test_resources import \
    TestCaseBase, args_constructor_for
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _NoLineMatchesRegEx(),
        _ALineMatchesRegEx(),
        _EveryLineMatchesRegEx(),
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
            quantifier=Quantifier.ALL,
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
            expected_result_of_positive_test=PassOrFail.FAIL,
            quantifier=Quantifier.ALL,
            actual_file_contents=actual_contents,
        )


class _EveryLineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['the first MATCH',
                                         'the MATCH again',
                                         'MATCH finally'])
        regex_arg_str = syntax_for_regex_matcher('.*MATCH')
        self._check_variants_with_expectation_type(
            args_constructor_for(line_matcher=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            quantifier=Quantifier.ALL,
            actual_file_contents=actual_contents,
        )
