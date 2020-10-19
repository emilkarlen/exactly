import unittest
from typing import List, TypeVar, Generic

from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers.multi_range import test_resources as sut
from exactly_lib_test.test_resources.test_utils import InpExp


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCaseCalculationOfExpectedLines),
        unittest.makeSuite(TestCaseCalculationOfMaxNumAccessedLines),
    ])


EXPECTED = TypeVar('EXPECTED')


class Case(Generic[EXPECTED]):
    def __init__(self,
                 name: str,
                 case: sut.Case,
                 input_cases: List[InpExp[List[str], EXPECTED]]
                 ):
        self.name = name
        self.case = case
        self.input_cases = input_cases


class TestCaseCalculationOfExpectedLines(unittest.TestCase):
    def test_w_upper_limit(self):
        # ARRANGE #
        cases = [
            Case('empty',
                 w_upper_limit([]),
                 [
                     InpExp([], []),
                     InpExp(['1'], []),
                     InpExp(['1', '2'], []),
                 ]
                 ),
            Case('single, first element',
                 w_upper_limit([1]),
                 [
                     InpExp([], []),
                     InpExp(['1'], ['1']),
                     InpExp(['1', '2'], ['1']),
                 ]
                 ),
            Case('single, non-first element',
                 w_upper_limit([2]),
                 [
                     InpExp([], []),
                     InpExp(['1'], []),
                     InpExp(['1', '2'], ['2']),
                     InpExp(['1', '2', '3'], ['2']),
                 ]
                 ),
            Case('multiple, first is first element',
                 w_upper_limit([1, 3]),
                 [
                     InpExp([], []),
                     InpExp(['1'], ['1']),
                     InpExp(['1', '2'], ['1']),
                     InpExp(['1', '2', '3'], ['1', '3']),
                     InpExp(['1', '2', '3', '4'], ['1', '3']),
                 ]
                 ),
            Case('multiple, first is non-first element',
                 w_upper_limit([2, 3]),
                 [
                     InpExp([], []),
                     InpExp(['1'], []),
                     InpExp(['1', '2'], ['2']),
                     InpExp(['1', '2', '3'], ['2', '3']),
                     InpExp(['1', '2', '3', '4'], ['2', '3']),
                 ]
                 ),
        ]

        self._check(cases)

    def test_wo_upper_limit(self):
        # ARRANGE #
        cases = [
            Case('single, first element',
                 wo_upper_limit([1]),
                 [
                     InpExp([], []),
                     InpExp(['1'], ['1']),
                     InpExp(['1', '2'], ['1', '2']),
                     InpExp(['1', '2', '3'], ['1', '2', '3']),
                 ]
                 ),
            Case('single, non-first element',
                 wo_upper_limit([2]),
                 [
                     InpExp([], []),
                     InpExp(['1'], []),
                     InpExp(['1', '2'], ['2']),
                     InpExp(['1', '2', '3'], ['2', '3']),
                 ]
                 ),
            Case('multiple, first is first element',
                 wo_upper_limit([1, 3]),
                 [
                     InpExp([], []),
                     InpExp(['1'], ['1']),
                     InpExp(['1', '2'], ['1']),
                     InpExp(['1', '2', '3'], ['1', '3']),
                     InpExp(['1', '2', '3', '4'], ['1', '3', '4']),
                     InpExp(['1', '2', '3', '4', '5'], ['1', '3', '4', '5']),
                 ]
                 ),
            Case('multiple, first is non-first element',
                 wo_upper_limit([2, 3]),
                 [
                     InpExp([], []),
                     InpExp(['1'], []),
                     InpExp(['1', '2'], ['2']),
                     InpExp(['1', '2', '3'], ['2', '3']),
                     InpExp(['1', '2', '3', '4'], ['2', '3', '4']),
                     InpExp(['1', '2', '3', '4', '5'], ['2', '3', '4', '5']),
                 ]
                 ),
        ]

        self._check(cases)

    def _check(self, cases: List[Case[List[str]]]):
        for case in cases:
            for input_case in case.input_cases:
                with self.subTest(case.name, input_case=input_case.input):
                    # ACT #
                    actual = case.case.expected_output_for_input(input_case.input)
                    # ASSERT #
                    self.assertEqual(input_case.expected, actual)


class TestCaseCalculationOfMaxNumAccessedLines(unittest.TestCase):
    def test_w_upper_limit(self):
        # ARRANGE #
        lines_in_range_cases = [
            [1],
            [2],
            [1, 3],
            [2, 3],
        ]
        input_lines_cases = [
            [],
            ['1'],
            ['1', '2'],
            ['1', '2', '3'],
            ['1', '2', '3', '4'],
            ['1', '2', '3', '4', '5'],
        ]
        for lines_in_range_case in lines_in_range_cases:
            case_to_check = w_upper_limit(lines_in_range_case)
            for input_lines_case in input_lines_cases:
                with self.subTest(lines_in_range_case=lines_in_range_case,
                                  input_lines_case=input_lines_case):
                    # ACT #
                    actual = case_to_check.max_lines_accessed_for_input(input_lines_case)
                    # ASSERT #
                    expected = min(len(input_lines_case),
                                   case_to_check.lines_in_ranges__increasing[-1])
                    self.assertEqual(expected, actual)

    def test_wo_upper_limit(self):
        # ARRANGE #
        lines_in_range_cases = [
            [1],
            [2],
            [1, 3],
            [2, 3],
        ]
        input_lines_cases = [
            [],
            ['1'],
            ['1', '2'],
            ['1', '2', '3'],
            ['1', '2', '3', '4'],
            ['1', '2', '3', '4', '5'],
        ]
        for lines_in_range_case in lines_in_range_cases:
            case_to_check = wo_upper_limit(lines_in_range_case)
            for input_lines_case in input_lines_cases:
                with self.subTest(lines_in_range_case=lines_in_range_case,
                                  input_lines_case=input_lines_case):
                    # ACT #
                    actual = case_to_check.max_lines_accessed_for_input(input_lines_case)
                    # ASSERT #
                    self.assertEqual(len(input_lines_case), actual)

    def _check(self, cases: List[Case[int]]):
        for case in cases:
            for input_case in case.input_cases:
                with self.subTest(case.name, input_case=input_case.input):
                    # ACT #
                    actual = case.case.max_lines_accessed_for_input(input_case.input)
                    # ASSERT #
                    self.assertEqual(input_case.expected, actual)


def w_upper_limit(lines_in_ranges__increasing: List[int]) -> sut.Case:
    return sut.Case.w_upper_limit('', [], lines_in_ranges__increasing)


def wo_upper_limit(lines_in_ranges__increasing: List[int]) -> sut.Case:
    return sut.Case.wo_upper_limit('', [], lines_in_ranges__increasing)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
