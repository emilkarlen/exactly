import unittest
from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.case_generator import \
    SingleCaseGenerator, ExecutionResult, FullExecutionResult, ValidationFailure, MultipleExecutionCasesGenerator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, ParseExpectation, \
    ExecutionExpectation, Arrangement
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def execute_single(put: unittest.TestCase,
                   case: SingleCaseGenerator,
                   ):
    integration_check.CHECKER.check(
        put,
        source=case.arguments().as_remaining_source,
        model_constructor=
        integration_check.file_in_tcds(
            case.model_file.location,
            case.model_file.name,
        ),
        arrangement=
        Arrangement(
            tcds=case.tcds_arrangement(),
            symbols=case.symbols(put),
        ),
        expectation=
        Expectation(
            ParseExpectation(
                symbol_references=asrt.matches_sequence(case.expected_symbols())
            ),
            _execution_expectation_of(case.execution_result())
        )
    )


def execute_list(put: unittest.TestCase,
                 cases: Sequence[NameAndValue[SingleCaseGenerator]]):
    for case in cases:
        with put.subTest(case.name):
            execute_single(put, case.value)


def execute_multi(put: unittest.TestCase,
                  generator: MultipleExecutionCasesGenerator):
    integration_check.CHECKER.check_multi(
        put,
        generator.arguments().as_arguments,
        parse_expectation=ParseExpectation(
            symbol_references=asrt.matches_sequence(generator.expected_symbols())
        ),
        model_constructor=
        integration_check.file_in_tcds(
            generator.model_file.location,
            generator.model_file.name,
        ),
        execution=[
            NExArr(
                case.name,
                _execution_expectation_of(case.expected),
                case.arrangement,
            )
            for case in generator.execution_cases()
        ],
    )


def _execution_expectation_of(expected: ExecutionResult) -> ExecutionExpectation:
    if isinstance(expected, FullExecutionResult):
        return ExecutionExpectation(
            main_result=asrt_matching_result.matches_value(expected.is_match)
        )
    elif isinstance(expected, ValidationFailure):
        return ExecutionExpectation(
            validation=validation.ValidationAssertions.of_expectation(expected.expectation)
        )
    raise ValueError(
        'Unknown {}: {}'.format(
            str(type(ExecutionResult)),
            expected,
        )
    )
