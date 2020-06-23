import unittest
from typing import Callable, Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.files_matcher.impl.matches.common import \
    MATCHES_NON_FULL__STRUCTURE_NAME, MATCHES_FULL__STRUCTURE_NAME
from exactly_lib.type_system.logic.files_matcher import FilesMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.file_matcher.test_resources import file_matchers
from exactly_lib_test.test_case_utils.files_condition.test_resources.arguments_building import FilesConditionArg
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import ModelConstructor
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import PrimAndExeExpectation, Arrangement, \
    Expectation, ExecutionExpectation
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


class MatcherCase:
    def __init__(self,
                 name: str,
                 arguments_for_fc: Callable[[FilesConditionArg], FilesMatcherArg],
                 ):
        self.name = name
        self.arguments_for_fc = arguments_for_fc


FULL_AND_NON_FULL_CASES = [
    MatcherCase(
        MATCHES_NON_FULL__STRUCTURE_NAME,
        args.matches_non_full,
    ),
    MatcherCase(
        MATCHES_FULL__STRUCTURE_NAME,
        args.matches_full,
    ),
]


def check_non_full_and_full(
        put: unittest.TestCase,
        files_condition_argument: FilesConditionArg,
        model: ModelConstructor,
        arrangement: Arrangement,
        expectation: Expectation[FilesMatcher, bool],
):
    for case in FULL_AND_NON_FULL_CASES:
        with put.subTest(case.name):
            matcher_argument = case.arguments_for_fc(files_condition_argument)
            integration_check.CHECKER.check__w_source_variants(
                put,
                matcher_argument.as_arguments,
                model,
                arrangement,
                _trace_for_matcher(case.name, expectation),
            )


def check_non_full_and_full__multi(
        put: unittest.TestCase,
        files_condition_argument: FilesConditionArg,
        symbol_references: ValueAssertion[Sequence[SymbolReference]],
        model: ModelConstructor,
        execution: Sequence[NExArr[PrimAndExeExpectation[FilesMatcher, bool],
                                   Arrangement]],

):
    for case in FULL_AND_NON_FULL_CASES:
        execution_w_trace_assertion = [
            n_ex_arr.translate(lambda pee: prim_and_exe_w_header_matcher(case.name, pee),
                               lambda x: x)
            for n_ex_arr in execution
        ]

        with put.subTest(case.name):
            matcher_argument = case.arguments_for_fc(files_condition_argument)
            integration_check.CHECKER.check_multi__w_source_variants(
                put,
                matcher_argument.as_arguments,
                symbol_references,
                model,
                execution_w_trace_assertion,
            )


def _trace_for_matcher(matcher_name: str,
                       original: Expectation[FilesMatcher, bool],
                       ) -> Expectation[FilesMatcher, MatchingResult]:
    return Expectation(
        original.parse,
        exe_w_added_header_matcher(matcher_name, original.execution),
        original.primitive,
    )


def prim_and_exe_w_header_matcher(matcher_name: str,
                                  original: PrimAndExeExpectation[FilesMatcher, bool],
                                  ) -> PrimAndExeExpectation[FilesMatcher, MatchingResult]:
    return PrimAndExeExpectation(
        exe_w_added_header_matcher(matcher_name, original.execution),
        original.primitive,
    )


def exe_w_added_header_matcher(matcher_header: str,
                               original: ExecutionExpectation[bool],
                               ) -> ExecutionExpectation[MatchingResult]:
    return ExecutionExpectation(
        original.validation,
        asrt_matching_result.matches_value__w_header(
            value=original.main_result,
            header=asrt.equals(matcher_header)
        ),
        original.is_hard_error,
    )


class Case:
    def __init__(self,
                 name: str,
                 files_condition: FilesConditionArg,
                 arrangement: Arrangement,
                 expectation: Expectation[FilesMatcher, bool],
                 ):
        self.name = name
        self.files_condition = files_condition
        self.expectation = expectation
        self.arrangement = arrangement


NON_MATCHING_EXECUTION_EXPECTATION = ExecutionExpectation(
    main_result=asrt.equals(False)
)
MATCHING_EXECUTION_EXPECTATION = ExecutionExpectation(
    main_result=asrt.equals(True)
)


def is_regular_file_matcher(symbol_name: str) -> FileMatcherSymbolContext:
    return FileMatcherSymbolContext.of_primitive(
        symbol_name,
        file_matchers.IsRegularFileMatcher()
    )


def is_dir_file_matcher(symbol_name: str) -> FileMatcherSymbolContext:
    return FileMatcherSymbolContext.of_primitive(
        symbol_name,
        file_matchers.IsDirectoryMatcher()
    )


IS_REGULAR_FILE_FILE_MATCHER = is_regular_file_matcher('is_regular_file')

IS_DIR_FILE_MATCHER = is_dir_file_matcher('is_dir')

IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS = SymbolContext.symbol_table_of_contexts([
    IS_REGULAR_FILE_FILE_MATCHER,
    IS_DIR_FILE_MATCHER,
])
