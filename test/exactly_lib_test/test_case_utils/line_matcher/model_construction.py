import unittest
from typing import List, Sequence

from exactly_lib.test_case_utils.line_matcher import model_construction as sut
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.util.interval import int_interval as ivs
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib.util.interval.w_inversion import intervals as i_ivs
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib_test.test_case_utils.line_matcher.test_resources.model_assertions import matches_line
from exactly_lib_test.test_case_utils.line_matcher.test_resources.model_construction import check_cases, ModelSetup, \
    OutputCase, ExecutionExpectation
from exactly_lib_test.test_resources.test_utils import NArrEx, ArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.interval.test_resources import interval_assertion as asrt_interval


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestAdaptToLineNumRange),
        TestLinesIterable(),
        TestLinesIterableForIntervalForModelWNumElements0(),
        unittest.makeSuite(TestLinesIterableForIntervalForModelWNumElements1),
        unittest.makeSuite(TestLinesIterableForIntervalForModelWNumElements10),
    ])


class TestAdaptToLineNumRange(unittest.TestCase):
    def test_identical(self):
        self._check([
            _identical('empty', i_ivs.Empty()),
            _identical('unlimited', i_ivs.Unlimited()),
            _identical('point', i_ivs.point(sut.FIRST_LINE_NUMBER + 1)),
            _identical('upper limit', i_ivs.UpperLimit(5)),
            _identical('upper limit (1st line)', i_ivs.UpperLimit(sut.FIRST_LINE_NUMBER)),
            _identical('lower limit', i_ivs.LowerLimit(7)),
            _identical('finite', i_ivs.Finite(3, 5)),
        ])

    def test_non_identical_point(self):
        self._check([
            NArrEx('point before 1st line',
                   i_ivs.point(-1),
                   i_ivs.Empty()
                   ),
            NArrEx('point before 1st line',
                   i_ivs.point(0),
                   i_ivs.Empty()
                   ),
            NArrEx('point is 1st line',
                   i_ivs.point(sut.FIRST_LINE_NUMBER),
                   i_ivs.UpperLimit(sut.FIRST_LINE_NUMBER),
                   ),
        ])

    def test_non_identical_upper_limit(self):
        self._check([
            NArrEx('upper limit before 1st line',
                   i_ivs.UpperLimit(-1),
                   i_ivs.Empty()
                   ),
            NArrEx('upper limit before 1st line',
                   i_ivs.UpperLimit(0),
                   i_ivs.Empty()
                   ),
        ])

    def test_non_identical_lower_limit(self):
        self._check([
            NArrEx('lower limit before 1st line',
                   i_ivs.LowerLimit(-1),
                   i_ivs.Unlimited()
                   ),
            NArrEx('lower limit before 1st line',
                   i_ivs.LowerLimit(0),
                   i_ivs.Unlimited()
                   ),
            NArrEx('lower limit is 1st line',
                   i_ivs.LowerLimit(sut.FIRST_LINE_NUMBER),
                   i_ivs.Unlimited()
                   ),
        ])

    def test_non_identical_finite(self):
        self._check([
            _anonymous(
                i_ivs.Finite(-2, -1),
                i_ivs.Empty()
            ),
            _anonymous(
                i_ivs.Finite(-2, 0),
                i_ivs.Empty()
            ),
            _anonymous(
                i_ivs.Finite(-2, 1),
                i_ivs.UpperLimit(1)
            ),
            _anonymous(
                i_ivs.Finite(-2, 2),
                i_ivs.UpperLimit(2)
            ),
            _anonymous(
                i_ivs.Finite(-1, 2),
                i_ivs.UpperLimit(2)
            ),
            _anonymous(
                i_ivs.Finite(0, 2),
                i_ivs.UpperLimit(2)
            ),
            _anonymous(
                i_ivs.Finite(1, 2),
                i_ivs.UpperLimit(2)
            ),
        ])

    def _check(self, cases: Sequence[NArrEx[IntIntervalWInversion, IntIntervalWInversion]]):
        # ARRANGE #
        for case in cases:
            with self.subTest(case.name,
                              interval=str(case.arrangement)):
                # ACT #
                actual = sut.adapt_to_line_num_range(case.arrangement)
                # ASSERT #
                expectation = asrt_interval.equals_interval(case.expectation)
                expectation.apply_without_message(self, actual)


class Case:
    def __init__(self,
                 name: str,
                 input_source_lines: List[str],
                 expected: List[LineMatcherLine],
                 ):
        self.name = name
        self.input_source_lines = input_source_lines
        self.expected = expected


class TestLinesIterable(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            Case('empty input should give empty list of models',
                 input_source_lines=[],
                 expected=[]
                 ),

            Case('first line number should be 1',
                 input_source_lines=['a'],
                 expected=[(1, 'a')]
                 ),

            Case('trailing newline should be removed',
                 input_source_lines=['a\n'],
                 expected=[(1, 'a')]
                 ),

            Case('trailing newline should be removed, but not space before it',
                 input_source_lines=['a \n'],
                 expected=[(1, 'a ')]
                 ),

            Case('trailing non-newline space should be removed',
                 input_source_lines=['a  '],
                 expected=[(1, 'a  ')]
                 ),

            Case('space at start of line should be preserved',
                 input_source_lines=[' a'],
                 expected=[(1, ' a')]
                 ),

            Case('lines should be numbered 1,2,3, ...',
                 input_source_lines=['a\n',
                                     'b\n',
                                     'c\n',
                                     'd'],
                 expected=[(1, 'a'),
                           (2, 'b'),
                           (3, 'c'),
                           (4, 'd'),
                           ]
                 ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = sut.model_iter_from_file_line_iter(case.input_source_lines)
                # ASSERT #
                actual_list = list(actual)
                self.assertEqual(case.expected,
                                 actual_list)


class TestLinesIterableForIntervalForModelWNumElements0(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model = ()
        interval_cases = [
            ivs.Empty(),
            ivs.point(1),
            ivs.point(2),
            ivs.finite(1, 2),
            ivs.finite(1, 3),
            ivs.upper_limit(1),
            ivs.upper_limit(2),
            ivs.lower_limit(2),
            ivs.unlimited(),
        ]
        cases = [
            ArrEx(interval, ExecutionExpectation(0, asrt.is_empty_sequence))
            for interval in interval_cases
        ]
        # ACT & ASSERT #
        check_cases(self, model, cases)


class IntervalAndNumLinesFromIter:
    def __init__(self,
                 interval: IntInterval,
                 max_num_lines_from_iter: int,
                 ):
        self.interval = interval
        self.max_num_lines_from_iter = max_num_lines_from_iter


class TestLinesIterableForIntervalForModelWNumElements1(unittest.TestCase):
    MODEL = ['the line contents']

    def test_empty_output(self):
        # ARRANGE #
        interval_cases = [
            IntervalAndNumLinesFromIter(ivs.Empty(), 0),
            IntervalAndNumLinesFromIter(ivs.point(2), 1),
            IntervalAndNumLinesFromIter(ivs.lower_limit(2), 1),
        ]
        cases = [
            ArrEx(interval.interval,
                  ExecutionExpectation(interval.max_num_lines_from_iter,
                                       asrt.is_empty_sequence))
            for interval in interval_cases
        ]
        # ACT & ASSERT #
        check_cases(self, self.MODEL, cases)

    def test_non_empty_output(self):
        # ARRANGE #
        interval_cases = [
            ivs.point(1),
            ivs.finite(1, 2),
            ivs.finite(1, 3),
            ivs.upper_limit(1),
            ivs.upper_limit(2),
            ivs.unlimited(),
        ]
        cases = [
            ArrEx(interval,
                  ExecutionExpectation(1,
                                       asrt.matches_singleton_sequence(matches_line(1, self.MODEL[0])))
                  )
            for interval in interval_cases
        ]
        # ACT & ASSERT #
        check_cases(self, self.MODEL, cases)


class TestLinesIterableForIntervalForModelWNumElements10(unittest.TestCase):
    MODEL_SETUP = ModelSetup([
        'Line {}\n'.format(n + 1)
        for n in range(10)
    ])

    def test_empty(self):
        self.MODEL_SETUP.check_output_is_empty(self, ivs.Empty(), 0)

    def test_unlimited(self):
        self.MODEL_SETUP.check_output_is_every_line(self, ivs.unlimited())

    def test_point(self):
        self.MODEL_SETUP.check_output_cases(
            self,
            [
                OutputCase.non_empty(2, 2, 2, [ivs.point(2)]),
                OutputCase.non_empty(9, 9, 9, [ivs.point(9)]),
                OutputCase.non_empty(10, 10, 10, [ivs.point(10)]),
                OutputCase.empty(10, [ivs.point(11)]),
            ]
        )

    def test_finite(self):
        self.MODEL_SETUP.check_output_cases(
            self,
            [
                OutputCase.non_empty(2, 3, 3, [ivs.finite(2, 3)]),
                OutputCase.non_empty(3, 10, 10, [ivs.finite(3, 10), ivs.finite(3, 11)]),
                OutputCase.non_empty(10, 10, 10, [ivs.finite(10, 11), ivs.finite(10, 12)]),
                OutputCase.empty(10, [ivs.finite(11, 12)]),
            ]
        )

    def test_upper(self):
        self.MODEL_SETUP.check_output_cases(
            self,
            [
                OutputCase.non_empty(1, 2, 2, [ivs.upper_limit(2)]),
                OutputCase.non_empty(1, 5, 5, [ivs.upper_limit(5)]),
                OutputCase.non_empty(1, 10, 10, [ivs.upper_limit(10), ivs.upper_limit(11), ivs.upper_limit(12)]),
            ]
        )

    def test_lower(self):
        self.MODEL_SETUP.check_output_cases(
            self,
            [
                OutputCase.non_empty(2, 10, 10, [ivs.lower_limit(2)]),
                OutputCase.non_empty(5, 10, 10, [ivs.lower_limit(5)]),
                OutputCase.non_empty(10, 10, 10, [ivs.lower_limit(10)]),
                OutputCase.empty(10, [ivs.lower_limit(11), ivs.lower_limit(12)]),
            ]
        )


def _identical(name: str, input_: IntIntervalWInversion,
               ) -> NArrEx[IntIntervalWInversion, IntIntervalWInversion]:
    return NArrEx('identical ' + name, input_, input_)


def _anonymous(input_: IntIntervalWInversion,
               expected: IntIntervalWInversion,
               ) -> NArrEx[IntIntervalWInversion, IntIntervalWInversion]:
    return NArrEx(str(input_), input_, expected)
