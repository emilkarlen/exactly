import itertools
import unittest
from typing import Sequence, Tuple, Optional

from exactly_lib.impls.types.line_matcher import model_construction as sut
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib_test.impls.types.line_matcher.test_resources.model_assertions import matches_lines
from exactly_lib_test.test_resources.iterator import IteratorWCheckOfMaxNumRequestedElements
from exactly_lib_test.test_resources.test_utils import ArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion

LineAndModel = Tuple[str, LineMatcherLine]


class ExecutionExpectation:
    def __init__(self,
                 max_num_lines_from_iter: int,
                 result: Assertion[Sequence[LineAndModel]],
                 ):
        self.max_num_lines_from_iter = max_num_lines_from_iter
        self.result = result


class OutputCase:
    def __init__(self,
                 max_num_lines_from_iter: int,
                 expected_output_lines: Optional[Tuple[int, int]],
                 equivalent_intervals: Sequence[IntInterval],
                 ):
        self.max_num_lines_from_iter = max_num_lines_from_iter
        self.expected_output_lines = expected_output_lines
        self.equivalent_intervals = equivalent_intervals

    @staticmethod
    def non_empty(first_line_num: int,
                  last_line_num: int,
                  max_num_lines_from_iter: int,
                  equivalent_intervals: Sequence[IntInterval],
                  ) -> 'OutputCase':
        return OutputCase(max_num_lines_from_iter,
                          (first_line_num, last_line_num),
                          equivalent_intervals)

    @staticmethod
    def empty(
            max_num_lines_from_iter: int,
            equivalent_intervals: Sequence[IntInterval]) -> 'OutputCase':
        return OutputCase(max_num_lines_from_iter, None, equivalent_intervals)


class ModelSetup:
    def __init__(self, model: Sequence[str]):
        self.model = model

    def matches_lines(self,
                      first_line_num: int,
                      last_line_num: int,
                      ) -> Assertion[Sequence[LineAndModel]]:
        lines_full_contents = self.model[first_line_num - 1:last_line_num]
        return matches_lines(first_line_num, lines_full_contents)

    def matches_lines__mb_empty(self,
                                expected_output_lines: Optional[Tuple[int, int]],
                                ) -> Assertion[Sequence[LineAndModel]]:
        return (
            asrt.is_empty_sequence
            if expected_output_lines is None
            else self.matches_lines(expected_output_lines[0], expected_output_lines[1])
        )

    def cases_for_output_case(self, output_case: OutputCase,
                              ) -> Sequence[ArrEx[IntInterval, ExecutionExpectation]]:
        return [
            ArrEx(interval,
                  ExecutionExpectation(
                      output_case.max_num_lines_from_iter,
                      self.matches_lines__mb_empty(output_case.expected_output_lines))
                  )
            for interval in output_case.equivalent_intervals

        ]

    def cases_for_output_cases(self,
                               output_cases: Sequence[OutputCase],
                               ) -> Sequence[ArrEx[IntInterval, ExecutionExpectation]]:
        return list(itertools.chain.from_iterable(
            [
                self.cases_for_output_case(output_case)
                for output_case in output_cases
            ]
        ))

    def check_output_is_empty(self,
                              put: unittest.TestCase,
                              interval: IntInterval,
                              max_num_lines_from_iter: int,
                              ):
        _check(put, self.model, interval, max_num_lines_from_iter, self.matches_lines__mb_empty(None))

    def check_output_is_every_line(self,
                                   put: unittest.TestCase,
                                   interval: IntInterval,
                                   ):
        num_model_elements = len(self.model)
        _check(put, self.model, interval, num_model_elements, self.matches_lines(1, num_model_elements))

    def check_output_cases(self,
                           put: unittest.TestCase,
                           cases: Sequence[OutputCase],
                           ):
        check_cases(
            put,
            self.model,
            self.cases_for_output_cases(cases)
        )


def _check(put: unittest.TestCase,
           model: Sequence[str],
           interval: IntInterval,
           max_num_lines_from_iter: int,
           expectation: Assertion[Sequence[LineAndModel]]
           ):
    # ACT #
    iterator_checker = IteratorWCheckOfMaxNumRequestedElements(put, max_num_lines_from_iter)
    actual = sut.original_and_model_iter_from_file_line_iter__interval(
        interval,
        iterator_checker.iterator_of(iter(model)),
    )
    # ASSERT #
    actual_as_list = list(actual)
    expectation.apply_without_message(put, actual_as_list)


def check_cases(put: unittest.TestCase,
                model: Sequence[str],
                cases: Sequence[ArrEx[IntInterval, ExecutionExpectation]],
                ):
    for case in cases:
        with put.subTest(str(case.arrangement)):
            _check(put,
                   model,
                   case.arrangement,
                   case.expectation.max_num_lines_from_iter,
                   case.expectation.result,
                   )
