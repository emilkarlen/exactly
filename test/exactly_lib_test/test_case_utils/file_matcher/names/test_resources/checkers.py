import unittest

from exactly_lib_test.test_case_utils.file_matcher.names.test_resources.configuration import Configuration
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import NameRegexVariant, \
    NameGlobPatternVariant
from exactly_lib_test.test_case_utils.file_matcher.test_resources.integration_check import ModelConstructor
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation
from exactly_lib_test.test_case_utils.regex.test_resources.assertions import is_regex_reference_restrictions
from exactly_lib_test.test_case_utils.test_resources import glob_pattern
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def check_glob(put: unittest.TestCase,
               conf: Configuration,
               pattern: str,
               model: ModelConstructor,
               expected_result: bool,
               ):
    pattern_string_symbol = StringSymbolContext.of_constant(
        'PATTERN_SYMBOL',
        pattern,
        default_restrictions=glob_pattern.is_glob_pattern_string_reference_restrictions()
    )
    arguments = conf.arguments(
        NameGlobPatternVariant(pattern_string_symbol.name__sym_ref_syntax)
    )

    integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
        put,
        arguments=arguments.as_arguments,
        input_=model,
        arrangement=arrangement_wo_tcds(
            symbols=pattern_string_symbol.symbol_table
        ),
        expectation=Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_sequence([
                    pattern_string_symbol.reference_assertion,
                ]),
            ),
            ExecutionExpectation(
                main_result=asrt_matching_result.matches_value__w_header(
                    asrt.equals(expected_result),
                    asrt.equals(conf.node_name)
                )
            ),
        )
    )


def check_regex(put: unittest.TestCase,
                conf: Configuration,
                pattern: str,
                ignore_case: bool,
                model: ModelConstructor,
                expected_result: bool,
                ):
    pattern_string_symbol = StringSymbolContext.of_constant(
        'PATTERN_SYMBOL',
        pattern,
        default_restrictions=is_regex_reference_restrictions()
    )
    arguments = conf.arguments(
        NameRegexVariant.of(pattern_string_symbol.name__sym_ref_syntax,
                            ignore_case=ignore_case)
    )

    integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
        put,
        arguments=arguments.as_arguments,
        input_=model,
        arrangement=arrangement_wo_tcds(
            symbols=pattern_string_symbol.symbol_table
        ),
        expectation=Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_sequence([
                    pattern_string_symbol.reference_assertion,
                ]),
            ),
            ExecutionExpectation(
                main_result=asrt_matching_result.matches_value__w_header(
                    asrt.equals(expected_result),
                    asrt.equals(conf.node_name)
                )
            ),
        )
    )
