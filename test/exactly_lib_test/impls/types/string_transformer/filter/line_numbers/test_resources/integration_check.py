import unittest
from typing import Sequence

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, arrangement_w_tcds
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources import \
    argument_building as range_args
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources.expectations import \
    InputAndExpected, expectation_of_successful_execution__check_only_as_lines, InputAndExpectedWExtDeps
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_building as args, integration_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def check__w_max_lines_from_iter(put: unittest.TestCase,
                                 range_expr: Sequence[range_args.Range],
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
                                                             range_expr: Sequence[range_args.Range],
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
                                                              range_expr: Sequence[range_args.Range],
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
                                            range_expr: Sequence[range_args.Range],
                                            input_and_expected: InputAndExpectedWExtDeps,
                                            ):
    arguments = args.filter_line_nums__multi(range_expr)
    for source_may_depend_on_external_resources in [False, True]:
        with put.subTest(may_depend_on_external_resources=source_may_depend_on_external_resources):
            integration_check.CHECKER__PARSE_SIMPLE.check(
                put,
                arguments.as_remaining_source,
                model_constructor.of_lines(
                    put,
                    input_and_expected.input,
                    may_depend_on_external_resources=source_may_depend_on_external_resources,
                ),
                arrangement_w_tcds(),
                integration_check.expectation_of_successful_execution(
                    symbol_references=asrt.is_empty_sequence,
                    output_lines=input_and_expected.expected.lines,
                    may_depend_on_external_resources=input_and_expected.expected.may_dep_on_ext_rsrc(
                        source_may_depend_on_external_resources),
                    frozen_may_depend_on_external_resources=asrt.anything_goes(),
                    is_identity_transformer=False,
                )
            )
