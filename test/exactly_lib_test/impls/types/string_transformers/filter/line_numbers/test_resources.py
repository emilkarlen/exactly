import unittest
from typing import List, Sequence

from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import Range, SingleLineRange, \
    LowerLimitRange, UpperLimitRange, LowerAndUpperLimitRange
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation, \
    ExecutionExpectation, prim_asrt__constant, arrangement_w_tcds, arrangement_wo_tcds
from exactly_lib_test.impls.types.string_model.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformers.test_resources.integration_check import StExpectation
from exactly_lib_test.test_resources.test_utils import InpExp
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.string.test_resources.string import \
    IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION
from exactly_lib_test.type_val_prims.string_model.test_resources import assertions
from exactly_lib_test.type_val_prims.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer

IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS = IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION

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
            main_result=assertions.matches__lines__check_just_as_lines(
                output_lines,
            ),
        ),
        prim_asrt__constant(
            asrt_string_transformer.is_identity_transformer(False)
        )
    )


def check__w_max_lines_from_iter(put: unittest.TestCase,
                                 range_expr: Sequence[args.Range],
                                 max_lines_from_iter: int,
                                 input_and_expected: InputAndExpected,
                                 ):
    arguments = args.filter_line_nums__multi(range_expr)
    integration_check.CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION.check(
        put,
        arguments.as_remaining_source,
        model_constructor.of_lines__w_max_invocations__w_max_lines_from_iter(
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


def check__w_max_as_lines_invocations__w_max_lines_from_iter(put: unittest.TestCase,
                                                             range_expr: Sequence[args.Range],
                                                             max_lines_from_iter: int,
                                                             max_as_lines_invocations: int,
                                                             input_and_expected: InputAndExpected,
                                                             ):
    arguments = args.filter_line_nums__multi(range_expr)
    integration_check.CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION.check(
        put,
        arguments.as_remaining_source,
        model_constructor.of_lines__w_max_invocations__w_max_lines_from_iter(
            put,
            input_and_expected.input,
            max_num_lines_from_iter=max_lines_from_iter,
            max_as_lines_invocations=max_as_lines_invocations,
        ),
        arrangement_wo_tcds(),
        expectation_of_successful_execution__check_only_as_lines(
            symbol_references=asrt.is_empty_sequence,
            output_lines=input_and_expected.expected,
        )
    )


def check__w_max_as_lines_invocations__wo_max_lines_from_iter(put: unittest.TestCase,
                                                              range_expr: Sequence[args.Range],
                                                              input_and_expected: InputAndExpected,
                                                              max_as_lines_invocations: int = 1,
                                                              ):
    arguments = args.filter_line_nums__multi(range_expr)
    integration_check.CHECKER__PARSE_SIMPLE__WO_IMPLICIT_MODEL_EVALUATION.check(
        put,
        arguments.as_remaining_source,
        model_constructor.of_lines__w_max_invocations(
            put,
            input_and_expected.input,
            max_as_lines_invocations,
        ),
        arrangement_wo_tcds(),
        expectation_of_successful_execution__check_only_as_lines(
            symbol_references=asrt.is_empty_sequence,
            output_lines=input_and_expected.expected,
        )
    )


def check__w_access_of_all_model_properties(put: unittest.TestCase,
                                            range_expr: Sequence[args.Range],
                                            input_and_expected: InputAndExpected,
                                            ):
    arguments = args.filter_line_nums__multi(range_expr)
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


def is_single(line_number: int) -> ValueAssertion[Range]:
    return asrt.is_instance_with(
        SingleLineRange,
        asrt.sub_component('line_number',
                           lambda x: x.line_number,
                           asrt.equals(line_number)
                           )
    )


def is_lower(lower_limit: int) -> ValueAssertion[Range]:
    return asrt.is_instance_with(
        LowerLimitRange,
        asrt.sub_component('lower_limit',
                           lambda x: x.lower_limit,
                           asrt.equals(lower_limit)
                           )
    )


def is_upper(upper_limit: int) -> ValueAssertion[Range]:
    return asrt.is_instance_with(
        UpperLimitRange,
        asrt.sub_component('upper_limit',
                           lambda x: x.upper_limit,
                           asrt.equals(upper_limit)
                           )
    )


def is_lower_and_upper(lower_limit: int,
                       upper_limit: int) -> ValueAssertion[Range]:
    return asrt.is_instance_with__many(
        LowerAndUpperLimitRange,
        [
            asrt.sub_component('lower_limit',
                               lambda x: x.lower_limit,
                               asrt.equals(lower_limit)
                               ),
            asrt.sub_component('upper_limit',
                               lambda x: x.upper_limit,
                               asrt.equals(upper_limit)
                               ),
        ]
    )
