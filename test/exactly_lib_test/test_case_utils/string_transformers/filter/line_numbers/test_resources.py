import unittest
from typing import List, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation, \
    ExecutionExpectation, prim_asrt__constant, arrangement_w_tcds, arrangement_wo_tcds
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import StExpectation
from exactly_lib_test.test_resources.test_utils import InpExp
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer

InputAndExpected = InpExp[List[str], List[str]]


def expectation_of_successful_execution__check_only_as_lines(
        output_lines: List[str],
        symbol_references: ValueAssertion[Sequence[SymbolReference]],
        source: ValueAssertion[ParseSource] = asrt.anything_goes(),
) -> StExpectation:
    return Expectation(
        ParseExpectation(
            source=source,
            symbol_references=symbol_references
        ),
        ExecutionExpectation(
            main_result=assertions.model_lines_lists_matches__check_just_as_lines(
                output_lines,
            ),
        ),
        prim_asrt__constant(
            asrt_string_transformer.is_identity_transformer(False)
        )
    )


def check_int_arg__w_max_lines_from_iter(put: unittest.TestCase,
                                         range_expr: args.Range,
                                         max_lines_from_iter: int,
                                         input_and_expected: InputAndExpected,
                                         ):
    arguments = args.filter_line_nums(range_expr)
    integration_check.CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION.check(
        put,
        arguments.as_remaining_source,
        model_constructor.of_lines__w_max_1_invocation__w_max_lines_from_iter(
            put,
            input_and_expected.input,
            max_num_lines_from_iter=max_lines_from_iter,
        ),
        arrangement_wo_tcds(),
        expectation_of_successful_execution__check_only_as_lines(
            symbol_references=asrt.is_empty_sequence,
            output_lines=input_and_expected.expected,
        )
    )


def check_int_arg__wo_max_lines_from_iter(put: unittest.TestCase,
                                          range_expr: args.Range,
                                          input_and_expected: InputAndExpected,
                                          ):
    arguments = args.filter_line_nums(range_expr)
    integration_check.CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION.check(
        put,
        arguments.as_remaining_source,
        model_constructor.of_lines__w_max_1_invocation(
            put,
            input_and_expected.input,
        ),
        arrangement_wo_tcds(),
        expectation_of_successful_execution__check_only_as_lines(
            symbol_references=asrt.is_empty_sequence,
            output_lines=input_and_expected.expected,
        )
    )


def check_int_arg__w_access_of_all_model_properties(put: unittest.TestCase,
                                                    range_expr: args.Range,
                                                    input_and_expected: InputAndExpected,
                                                    ):
    arguments = args.filter_line_nums(range_expr)
    for may_depend_on_external_resources in [False, True]:
        with put.subTest(may_depend_on_external_resources=may_depend_on_external_resources):
            integration_check.CHECKER__PARSE_SIMPLE.check(
                put,
                arguments.as_remaining_source,
                model_constructor.of_lines(
                    put,
                    input_and_expected.input,
                    may_depend_on_external_resources=may_depend_on_external_resources,
                ),
                arrangement_w_tcds(),
                integration_check.expectation_of_successful_execution(
                    symbol_references=asrt.is_empty_sequence,
                    output_lines=input_and_expected.expected,
                    may_depend_on_external_resources=may_depend_on_external_resources,
                    is_identity_transformer=False,
                )
            )
