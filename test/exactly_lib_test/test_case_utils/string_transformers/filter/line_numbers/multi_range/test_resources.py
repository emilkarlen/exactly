import unittest
from typing import List, Sequence, Callable

from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers import test_resources as tr
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources.argument_building import Range
from exactly_lib_test.test_resources.test_utils import InpExp


class Case:
    def __init__(self,
                 name: str,
                 range_args: List[Range],
                 lines_in_ranges__increasing: List[int],
                 all_lines_after: bool,
                 ):
        self.name = name
        self.range_args = range_args
        self.lines_in_ranges__increasing = lines_in_ranges__increasing
        self.all_lines_after = all_lines_after

    @staticmethod
    def w_upper_limit(
            name: str,
            ranges: List[Range],
            lines_in_ranges__increasing: List[int],
    ) -> 'Case':
        return Case(
            name,
            ranges,
            lines_in_ranges__increasing,
            False,
        )

    @staticmethod
    def wo_upper_limit(
            name: str,
            ranges: List[Range],
            lines_in_ranges__increasing: List[int],
    ) -> 'Case':
        return Case(
            name,
            ranges,
            lines_in_ranges__increasing,
            True,
        )

    def max_lines_accessed_for_input(self, input_: List[str]) -> int:
        if self.all_lines_after:
            return len(input_)
        else:
            if not self.lines_in_ranges__increasing:
                return 0
            else:
                return min(len(input_), self.lines_in_ranges__increasing[-1])

    def expected_output_for_input(self, input_: List[str]) -> List[str]:
        ret_val = []
        for line_num in self.lines_in_ranges__increasing:
            if len(input_) < line_num:
                break
            ret_val.append(input_[line_num - 1])

        if self.all_lines_after:
            max_limited_line_num = max(self.lines_in_ranges__increasing)
            ret_val += input_[max_limited_line_num:]

        return ret_val

    def inp_exp_of(self, input_: List[str]) -> InpExp[List[str], List[str]]:
        return InpExp(input_, self.expected_output_for_input(input_))


class CheckerOfConstInput:
    def __init__(self,
                 put: unittest.TestCase,
                 input_: List[str],
                 max_as_lines_invocations__when_only_checking_via_as_lines: int = 1,
                 ):
        self._put = put
        self.input = input_
        self.max_as_lines_invocations = max_as_lines_invocations__when_only_checking_via_as_lines

    def check__w_max_lines_from_iter(self,
                                     ranges: Sequence[args.Range],
                                     max_lines_accessed: int,
                                     expected: List[str],
                                     ):
        return tr.check__w_max_as_lines_invocations__w_max_lines_from_iter(
            self._put,
            ranges,
            max_lines_accessed,
            self.max_as_lines_invocations,
            InpExp(self.input, expected),
        )

    def check__w_max_lines_from_iter__cases(self, cases: Sequence[Case]):
        self._check_cases_helper(cases, self._check_case__w_max_lines_from_iter)

    def check__wo_max_lines_from_iter(self,
                                      ranges: Sequence[args.Range],
                                      expected: List[str],
                                      ):
        tr.check__w_max_as_lines_invocations__wo_max_lines_from_iter(
            self._put,
            ranges,
            InpExp(self.input, expected),
            self.max_as_lines_invocations,
        )

    def check__wo_max_lines_from_iter__cases(self, cases: Sequence[Case]):
        self._check_cases_helper(cases, self._check_case__wo_max_lines_from_iter)

    def check__w_access_of_all_model_properties(self,
                                                ranges: Sequence[args.Range],
                                                expected: List[str],
                                                ):
        tr.check__w_access_of_all_model_properties(
            self._put,
            ranges,
            InpExp(self.input, expected),
        )

    def check__w_access_of_all_model_properties__cases(self, cases: Sequence[Case]):
        self._check_cases_helper(cases, self._check_case__w_access_of_all_model_properties)

    def _check_cases_helper(self,
                            cases: Sequence[Case],
                            do_check: Callable[[Case], None],
                            ):
        for case in cases:
            with self._put.subTest(name=case.name,
                                   args=[str(r) for r in case.range_args]):
                do_check(case)

    def _check_case__w_access_of_all_model_properties(self, case: Case):
        self.check__w_access_of_all_model_properties(case.range_args,
                                                     case.expected_output_for_input(self.input))

    def _check_case__w_max_lines_from_iter(self, case: Case):
        expected = case.expected_output_for_input(self.input)
        max_lines_accessed = case.max_lines_accessed_for_input(self.input)
        self.check__w_max_lines_from_iter(case.range_args,
                                          max_lines_accessed,
                                          expected,
                                          )

    def _check_case__wo_max_lines_from_iter(self, case: Case):
        self.check__wo_max_lines_from_iter(case.range_args,
                                           case.expected_output_for_input(self.input),
                                           )


class TestCaseWCheckerOfConstInputBase(unittest.TestCase):
    def input(self) -> List[str]:
        raise NotImplementedError('abstract method')

    def max_as_lines_invocations__when_only_checking_via_as_lines(self) -> int:
        raise NotImplementedError('abstract method')

    @property
    def checker(self) -> CheckerOfConstInput:
        return CheckerOfConstInput(
            self,
            self.input(),
            self.max_as_lines_invocations__when_only_checking_via_as_lines()
        )
