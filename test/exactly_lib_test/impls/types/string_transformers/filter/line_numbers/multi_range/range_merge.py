"""
Test cases

* Positive number

 1      n (n+1)
|*--*---*|*---
| actual |

* Negative number

-(n+1) -n      -1
-----*|*----*---*|
      | actual   |
"""
import itertools
import unittest
from typing import Optional, List, Tuple

from exactly_lib.impls.types.string_transformer.impl.filter.line_nums import range_merge as sut
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import LowerAndUpperLimitRange, \
    Range, UpperLimitRange, LowerLimitRange, SingleLineRange
from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_merge import MergedRanges, FromTo
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources.expectations import \
    is_single, is_lower, \
    is_upper, is_lower_and_upper
from exactly_lib_test.test_resources.test_utils import NArrEx, ArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNonNegativeRanges),
        unittest.makeSuite(TestTranslationOfNegativeRanges),
    ])


class TestNonNegativeRanges(unittest.TestCase):
    def test_single_range(self):
        self._check_permutations([
            NArrEx(
                'no upper limits',
                [_single(3)],
                matches_merged_ranges(
                    head=asrt.is_none,
                    body=equals_segments([(3, 3)]),
                ),
            ),
            NArrEx(
                'single upper limit',
                [_to(5)],
                matches_merged_ranges(
                    head=asrt.equals(5),
                ),
            ),
            NArrEx(
                'single upper limit, and segment above',
                [_from(7)],
                matches_merged_ranges(
                    tail=asrt.equals(7),
                ),
            ),
            NArrEx(
                'multiple upper limits',
                [_from_to(13, 19)],
                matches_merged_ranges(
                    body=equals_segments([(13, 19)]),
                ),
            ),
            NArrEx(
                'single value 1 should become head',
                [_single(1)],
                matches_merged_ranges(
                    head=asrt.equals(1),
                ),
            ),
            NArrEx(
                'from-to starting at 1 should become head (upper bound 1)',
                [_from_to(1, 1)],
                matches_merged_ranges(
                    head=asrt.equals(1),
                ),
            ),
            NArrEx(
                'from-to starting at 1 should become head (upper bound > 1)',
                [_from_to(1, 2)],
                matches_merged_ranges(
                    head=asrt.equals(2),
                ),
            ),
        ])

    def test_merging_of__head(self):
        self._check_permutations([
            NArrEx(
                'multiple :N should become <head> w max of :Ns',
                [_to(5), _to(3), _to(7)],
                matches_merged_ranges(
                    head=asrt.equals(7),
                ),
            ),
            NArrEx(
                'M:Ns and Ns should be removed if covered by :Ns',
                [_to(7),
                 _from_to(2, 5), _from_to(1, 7),
                 _single(1), _single(7), _single(3),
                 ],
                matches_merged_ranges(
                    head=asrt.equals(7),
                ),
            ),
            NArrEx(
                '1:Ns should be translated to <head> (single)',
                [_from_to(1, 7)],
                matches_merged_ranges(
                    head=asrt.equals(7),
                ),
            ),
            NArrEx(
                '1:Ns should be translated to <head> (multiple)',
                [_from_to(1, 7), _from_to(1, 9)],
                matches_merged_ranges(
                    head=asrt.equals(9),
                ),
            ),
            NArrEx(
                '1:Ns should be translated to <head> (merge overlapping)',
                [_from_to(1, 7), _from_to(4, 9)],
                matches_merged_ranges(
                    head=asrt.equals(9),
                ),
            ),
            NArrEx(
                'overlapping M:N (single)',
                [_to(7), _from_to(3, 9)],
                matches_merged_ranges(
                    head=asrt.equals(9),
                ),
            ),
            NArrEx(
                'overlapping M:N (multiple)',
                [_to(7), _from_to(3, 9), _from_to(8, 12)],
                matches_merged_ranges(
                    head=asrt.equals(12),
                ),
            ),
            NArrEx(
                'adjacent M:N (single)',
                [_to(7), _from_to(8, 9)],
                matches_merged_ranges(
                    head=asrt.equals(9),
                ),
            ),
            NArrEx(
                'adjacent M:N (multiple)',
                [_to(7), _from_to(8, 9), _from_to(10, 12)],
                matches_merged_ranges(
                    head=asrt.equals(12),
                ),
            ),
            NArrEx(
                'adjacent N (single)',
                [_to(7), _single(8)],
                matches_merged_ranges(
                    head=asrt.equals(8),
                ),
            ),
            NArrEx(
                'adjacent N (multiple)',
                [_to(8), _single(9), _single(10)],
                matches_merged_ranges(
                    head=asrt.equals(10),
                ),
            ),
            NArrEx(
                'not merged N',
                [_to(8), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(8),
                    body=equals_segments([(12, 12)])
                ),
            ),
            NArrEx(
                'not merged M:N',
                [_to(8), _from_to(12, 13)],
                matches_merged_ranges(
                    head=asrt.equals(8),
                    body=equals_segments([(12, 13)])
                ),
            ),
            NArrEx(
                '1:N (all segments merged)',
                [_from_to(1, 2), _from_to(3, 4)],
                matches_merged_ranges(
                    head=asrt.equals(4),
                ),
            ),
            NArrEx(
                '1:N (some segments merged)',
                [_from_to(1, 2), _from_to(3, 4), _from_to(12, 13)],
                matches_merged_ranges(
                    head=asrt.equals(4),
                    body=equals_segments([(12, 13)])
                ),
            ),
        ])

    def test_merging_of__tail(self):
        self._check_permutations([
            NArrEx(
                'multiple N: should become <tail> w min of N:s',
                [_from(3), _from(5), _from(7)],
                matches_merged_ranges(
                    tail=asrt.equals(3),
                ),
            ),
            NArrEx(
                'M:Ns and Ns should be removed if covered by N:s',
                [_from(7),
                 _from_to(9, 12), _from_to(7, 8),
                 _single(7), _single(8)
                 ],
                matches_merged_ranges(
                    tail=asrt.equals(7),
                ),
            ),
            NArrEx(
                'overlapping M:N (single)',
                [_from(7), _from_to(3, 9)],
                matches_merged_ranges(
                    tail=asrt.equals(3),
                ),
            ),
            NArrEx(
                'overlapping M:N (multiple)',
                [_from(13), _from_to(9, 14), _from_to(5, 10)],
                matches_merged_ranges(
                    tail=asrt.equals(5),
                ),
            ),
            NArrEx(
                'adjacent M:N (single)',
                [_from(7), _from_to(4, 6)],
                matches_merged_ranges(
                    tail=asrt.equals(4),
                ),
            ),
            NArrEx(
                'adjacent M:N (multiple)',
                [_from(13), _from_to(9, 12), _from_to(7, 8)],
                matches_merged_ranges(
                    tail=asrt.equals(7),
                ),
            ),
            NArrEx(
                'adjacent N (single)',
                [_from(7), _single(6)],
                matches_merged_ranges(
                    tail=asrt.equals(6),
                ),
            ),
            NArrEx(
                'adjacent N (multiple)',
                [_from(13), _single(12), _single(11)],
                matches_merged_ranges(
                    tail=asrt.equals(11),
                ),
            ),
            NArrEx(
                'not merged N',
                [_from(8), _single(6)],
                matches_merged_ranges(
                    tail=asrt.equals(8),
                    body=equals_segments([(6, 6)])
                ),
            ),
            NArrEx(
                'not merged M:N',
                [_from(8), _from_to(5, 6)],
                matches_merged_ranges(
                    tail=asrt.equals(8),
                    body=equals_segments([(5, 6)])
                ),
            ),
        ])

    def test_merging_of__segments(self):
        self._check_permutations([
            NArrEx(
                'overlapping (single)',
                [_from_to(5, 7), _from_to(6, 8)],
                matches_merged_ranges(
                    body=equals_segments([(5, 8)])
                ),
            ),
            NArrEx(
                'overlapping (multiple)',
                [_from_to(5, 7), _from_to(6, 8), _from_to(7, 9)],
                matches_merged_ranges(
                    body=equals_segments([(5, 9)])
                ),
            ),
            NArrEx(
                'adjacent (single)',
                [_from_to(5, 7), _from_to(8, 9)],
                matches_merged_ranges(
                    body=equals_segments([(5, 9)])
                ),
            ),
            NArrEx(
                'adjacent (multiple)',
                [_from_to(5, 7), _single(8), _from_to(9, 10)],
                matches_merged_ranges(
                    body=equals_segments([(5, 10)])
                ),
            ),
            NArrEx(
                'subset (one range contains every other range (singles))',
                [_from_to(3, 7),
                 _single(3), _single(4), _single(7)],
                matches_merged_ranges(
                    body=equals_segments([(3, 7)])
                ),
            ),
            NArrEx(
                'subset (one range contains every other range (singles))',
                [_from_to(3, 7),
                 _from_to(3, 7), _from_to(3, 4), _from_to(5, 7), _from_to(4, 6)],
                matches_merged_ranges(
                    body=equals_segments([(3, 7)])
                ),
            ),
            NArrEx(
                'subset (merged ranges contains every other range)',
                [_from_to(3, 4), _from_to(5, 7),
                 _single(3), _single(7),
                 _from_to(3, 4), _from_to(4, 6)],
                matches_merged_ranges(
                    body=equals_segments([(3, 7)])
                ),
            ),
        ])

    def test_removal_of_emtpy_segments(self):
        self._check_permutations([
            NArrEx(
                'only empty ranges, involving 0 (multiple)',
                [_single(0), _to(0), _from_to(0, 0), _from_to(1, 0)],
                matches_merged_ranges(
                    is_empty=asrt.equals(True)
                ),
            ),
            NArrEx(
                'only empty ranges (single)',
                [_from_to(3, 2)],
                matches_merged_ranges(
                    is_empty=asrt.equals(True)
                ),
            ),
            NArrEx(
                'only empty ranges (multiple)',
                [_from_to(3, 2), _from_to(7, 2)],
                matches_merged_ranges(
                    is_empty=asrt.equals(True)
                ),
            ),
            NArrEx(
                'empty and non-empty ranges (from-to)',
                [_from_to(3, 2), _from_to(2, 7)],
                matches_merged_ranges(
                    body=equals_segments([(2, 7)]),
                ),
            ),
            NArrEx(
                'empty and non-empty ranges (single)',
                [_from_to(3, 2), _single(2)],
                matches_merged_ranges(
                    body=equals_segments([(2, 2)]),
                ),
            ),
            NArrEx(
                'empty and non-empty ranges (first-to)',
                [_from_to(3, 2), _to(2)],
                matches_merged_ranges(
                    head=asrt.equals(2),
                ),
            ),
            NArrEx(
                'empty and non-empty ranges (last-from)',
                [_from_to(3, 2), _from(2)],
                matches_merged_ranges(
                    tail=asrt.equals(2)
                ),
            ),
        ])

    def test_translation_of_0_for_non_empty_ranges(self):
        self._check_permutations([
            NArrEx(
                'everything',
                [_from(0)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True)
                ),
            ),
            NArrEx(
                'M:N',
                [_from_to(0, 10)],
                matches_merged_ranges(
                    head=asrt.equals(10)
                ),
            ),
        ])

    def test_merging_of__all_ranges_to_become_all_elements(self):
        self._check_permutations([
            NArrEx(
                '1:',
                [_from(1)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
            NArrEx(
                ':N N: (overlapping)',
                [_to(7), _from(7)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
            NArrEx(
                ':N (N+1): (adjacent)',
                [_to(7), _from(8)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
            NArrEx(
                '1:N N: (overlapping)',
                [_from_to(1, 7), _from(7)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
            NArrEx(
                '1:N (N+1): (adjacent)',
                [_from_to(1, 7), _from(8)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
            NArrEx(
                'head and tail merged with segments (overlapping)',
                [_to(3), _from_to(3, 12), _from(12)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
            NArrEx(
                'head and tail merged with segments (adjacent)',
                [_to(3), _from_to(4, 11), _from(12)],
                matches_merged_ranges(
                    is_everything=asrt.equals(True),
                ),
            ),
        ])

    def test_segments_should_be_sorted(self):
        self._check_permutations([
            NArrEx(
                'just segments (wo merge)',
                [_from_to(2, 4), _from_to(6, 9), _single(12)],
                matches_merged_ranges(
                    body=equals_segments([(2, 4), (6, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'just segments (w merge)',
                [_from_to(2, 4), _from_to(5, 6), _single(12)],
                matches_merged_ranges(
                    body=equals_segments([(2, 6), (12, 12)]),
                ),
            ),
            NArrEx(
                'with head',
                [_to(4), _from_to(6, 9), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(4),
                    body=equals_segments([(6, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with head and merge of head',
                [_to(4), _from_to(4, 5), _from_to(7, 9), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(5),
                    body=equals_segments([(7, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with head and merge of segments',
                [_to(3), _from_to(5, 6), _from_to(7, 9), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(3),
                    body=equals_segments([(5, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with tail',
                [_from(20), _from_to(6, 9), _single(12)],
                matches_merged_ranges(
                    tail=asrt.equals(20),
                    body=equals_segments([(6, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with tail and merge of tail',
                [_from_to(18, 20), _from(20), _from_to(6, 9), _single(12)],
                matches_merged_ranges(
                    tail=asrt.equals(18),
                    body=equals_segments([(6, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with tail and merge of segments',
                [_from(20), _from_to(6, 9), _single(10), _from_to(12, 14)],
                matches_merged_ranges(
                    tail=asrt.equals(20),
                    body=equals_segments([(6, 10), (12, 14)]),
                ),
            ),
            NArrEx(
                'with head and tail',
                [_to(4), _from(20), _from_to(6, 9), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(4),
                    tail=asrt.equals(20),
                    body=equals_segments([(6, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with head and tail, merge head',
                [_to(4), _from_to(4, 5), _from(20), _from_to(7, 9), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(5),
                    tail=asrt.equals(20),
                    body=equals_segments([(7, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with head and tail, merge tail',
                [_to(4), _from_to(18, 20), _from(20), _from_to(7, 9), _single(12)],
                matches_merged_ranges(
                    head=asrt.equals(4),
                    tail=asrt.equals(18),
                    body=equals_segments([(7, 9), (12, 12)]),
                ),
            ),
            NArrEx(
                'with head and tail, merge segments',
                [_to(4), _from(20), _from_to(7, 9), _from_to(11, 12), _single(13)],
                matches_merged_ranges(
                    head=asrt.equals(4),
                    tail=asrt.equals(20),
                    body=equals_segments([(7, 9), (11, 13)]),
                ),
            ),
        ])

    def _check_permutations(self, ranges_cases: List[NArrEx[List[Range], ValueAssertion[MergedRanges]]]):

        for ranges_case in ranges_cases:
            for permutation in itertools.permutations(ranges_case.arrangement):
                sequence = list(permutation)
                with self.subTest(ranges_case=ranges_case.name,
                                  sequence=[str(r) for r in sequence]):
                    # ACT #
                    actual = self._partition_and_merge__assert_no_negs(sequence)
                    # ASSERT #
                    ranges_case.expectation.apply_without_message(self, actual)

    def _partition_and_merge__assert_no_negs(self, ranges: List[Range]) -> MergedRanges:
        partitioning = sut.Partitioning([], [], [])
        negatives = sut.partition(ranges, partitioning)
        self.assertEqual(0, len(negatives), 'number of ranges w a negative value')
        return sut.merge(partitioning)


class TestTranslationOfNegativeRanges(unittest.TestCase):
    def test_single(self):
        # ARRANGE #
        num_lines = 10
        cases = [
            # N
            ArrEx(_single(-1), is_single(num_lines)),
            ArrEx(_single(-2), is_single(num_lines - 1)),
            ArrEx(_single(-num_lines), is_single(1)),
            ArrEx(_single(-num_lines - 1), is_single(0)),

            # :N
            ArrEx(_to(-1), is_upper(num_lines)),
            ArrEx(_to(-2), is_upper(num_lines - 1)),
            ArrEx(_to(-num_lines), is_upper(1)),
            ArrEx(_to(-num_lines - 1), is_upper(0)),

            # N:
            ArrEx(_from(-1), is_lower(num_lines)),
            ArrEx(_from(-2), is_lower(num_lines - 1)),
            ArrEx(_from(-num_lines), is_lower(1)),
            ArrEx(_from(-num_lines - 1), is_lower(0)),

            # M:N - only upper negative
            ArrEx(_from_to(0, -1), is_lower_and_upper(0, num_lines)),
            ArrEx(_from_to(1, -1), is_lower_and_upper(1, num_lines)),
            ArrEx(_from_to(1, -2), is_lower_and_upper(1, num_lines - 1)),
            ArrEx(_from_to(1, -num_lines), is_lower_and_upper(1, 1)),

            # M:N - only lower negative
            ArrEx(_from_to(-1, 0), is_lower_and_upper(num_lines, 0)),
            ArrEx(_from_to(-1, 5), is_lower_and_upper(num_lines, 5)),
            ArrEx(_from_to(-2, 5), is_lower_and_upper(num_lines - 1, 5)),
            ArrEx(_from_to(-num_lines, 5), is_lower_and_upper(1, 5)),

            # M:N - both lower and upper negative
            ArrEx(_from_to(-1, -1), is_lower_and_upper(num_lines, num_lines)),
            ArrEx(_from_to(-2, -5), is_lower_and_upper(num_lines - 1, 6)),
            ArrEx(_from_to(-num_lines, -num_lines), is_lower_and_upper(1, 1)),

            # M:N - lower out of range, upper non-neg
            ArrEx(_from_to(-num_lines - 1, 1), is_lower_and_upper(0, 1)),
            ArrEx(_from_to(-2 * num_lines, 0), is_lower_and_upper(0, 0)),

            # M:N - upper out of range, lower non-neg
            ArrEx(_from_to(1, -num_lines - 1), is_lower_and_upper(1, 0)),
            ArrEx(_from_to(0, -2 * num_lines), is_lower_and_upper(0, 0)),

            # M:N - lower and upper out of range
            ArrEx(_from_to(-num_lines - 1, -num_lines - 1), is_lower_and_upper(0, 0)),
            ArrEx(_from_to(-2 * num_lines, -num_lines - 1), is_lower_and_upper(0, 0)),
            ArrEx(_from_to(-num_lines - 1, -2 * num_lines), is_lower_and_upper(0, 0)),
        ]
        for case in cases:
            with self.subTest(str(case.arrangement)):
                # ACT #
                actual = sut.translate_neg_to_non_neg([case.arrangement], num_lines)
                # ASSERT #
                expectation = asrt.matches_singleton_sequence(case.expectation)
                expectation.apply_without_message(self, actual)

    def test_multiple(self):
        # ARRANGE #
        num_lines = 7
        cases = [
            # N
            ArrEx([
                _single(-1),
                _to(-1),
                _from(-num_lines - 1),
                _from_to(1, -num_lines),
                _from_to(-1, -num_lines - 1),
            ], [
                is_single(num_lines),
                is_upper(num_lines),
                is_lower(0),
                is_lower_and_upper(1, 1),
                is_lower_and_upper(num_lines, 0),
            ]),
        ]
        for case in cases:
            with self.subTest(str(case.arrangement)):
                # ACT #
                actual = sut.translate_neg_to_non_neg(case.arrangement, num_lines)
                # ASSERT #
                expectation = asrt.matches_sequence(case.expectation)
                expectation.apply_without_message(self, actual)


def _to(n: int) -> UpperLimitRange:
    return UpperLimitRange(n)


def _from(n: int) -> LowerLimitRange:
    return LowerLimitRange(n)


def _from_to(a: int, b: int) -> LowerAndUpperLimitRange:
    return LowerAndUpperLimitRange(a, b)


def _single(n: int) -> SingleLineRange:
    return SingleLineRange(n)


def equals_segments(segments: List[Tuple[int, int]]) -> ValueAssertion[List[FromTo]]:
    return asrt.matches_list([
        equals_segment(s[0], s[1])
        for s in segments
    ])


def equals_segment(a: int, b: int) -> ValueAssertion[FromTo]:
    return asrt.equals((a, b))


def matches_merged_ranges(head: ValueAssertion[Optional[int]] = asrt.is_none,
                          body: ValueAssertion[List[FromTo]] = asrt.is_empty,
                          tail: ValueAssertion[Optional[int]] = asrt.is_none,
                          is_everything: ValueAssertion[bool] = asrt.equals(False),
                          is_empty: ValueAssertion[bool] = asrt.equals(False),
                          ) -> ValueAssertion[MergedRanges]:
    return asrt.is_none_or_instance_with__many(
        MergedRanges,
        [
            asrt.sub_component(
                'head',
                _head,
                head,
            ),
            asrt.sub_component(
                'tail',
                _tail,
                tail,
            ),
            asrt.sub_component(
                'body',
                _body,
                body,
            ),
            asrt.sub_component(
                'is_everything',
                MergedRanges.is_everything,
                is_everything,
            ),
            asrt.sub_component(
                'is_empty',
                _is_empty,
                is_empty,
            ),
        ]
    )


def _head(x: MergedRanges) -> Optional[int]:
    return x.head


def _body(x: MergedRanges) -> List[FromTo]:
    return x.body


def _tail(x: MergedRanges) -> Optional[int]:
    return x.tail


def _is_empty(x: MergedRanges) -> bool:
    return x.is_empty


def _lu_lower(x: LowerAndUpperLimitRange) -> int:
    return x.lower_limit


def _lu_upper(x: LowerAndUpperLimitRange) -> int:
    return x.upper_limit


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
