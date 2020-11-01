import unittest
from typing import Sequence

from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.line_matcher import line_nums_interval
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher, FIRST_LINE_NUMBER
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib_test.test_case_utils.integer_matcher.test_resources import argument_building as im_args
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.line_matcher.test_resources import models
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, Expectation, \
    prim_asrt__constant
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as sm_args
from exactly_lib_test.test_case_utils.test_resources import arguments_building as arg_rend
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.argument_renderers import FileOrString
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.util.interval.test_resources import interval_assertion as asrt_interval


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestLineNumberPrimitive(),
        TestContentsPrimitive(),
        TestConstantPrimitive(),
        TestComposition(),
    ])


class TestLineNumberPrimitive(unittest.TestCase):
    def runTest(self):
        self._check_cases([
            NArrEx(
                'equals (within line-num-range)',
                im_args.comparison2(comparators.EQ, 2),
                asrt_interval.matches_point(2)
            ),
            NArrEx(
                'equals (outside line-num-range)',
                im_args.comparison2(comparators.EQ, -2),
                asrt_interval.matches_empty()
            ),
            NArrEx(
                'greater-than (within line-num-range)',
                im_args.comparison2(comparators.GT, 7),
                asrt_interval.matches_lower_limit(7 + 1)
            ),
            NArrEx(
                'greater-than (outside line-num-range)',
                im_args.comparison2(comparators.GTE, -7),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'greater-than-eq (FIRST-LINE-NUMBER)',
                im_args.comparison2(comparators.GTE, FIRST_LINE_NUMBER),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'greater-than && less-than (within line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        im_args.comparison2(comparators.GT, 7),
                        im_args.comparison2(comparators.LTE, 12),
                    ])
                ),
                asrt_interval.matches_finite(7 + 1, 12)
            ),
            NArrEx(
                'greater-than && less-than (outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        im_args.comparison2(comparators.GT, -7),
                        im_args.comparison2(comparators.LTE, 12),
                    ])
                ),
                asrt_interval.matches_upper_limit(12)
            ),
            NArrEx(
                'constant False',
                arg_rend.constant(False),
                asrt_interval.matches_empty()
            ),
            NArrEx(
                'constant False',
                arg_rend.constant(True),
                asrt_interval.matches_unlimited()
            ),
        ])

    def _check_cases(self,
                     cases: Sequence[NArrEx[ArgumentElementsRenderer, ValueAssertion[IntIntervalWInversion]]]):
        for case in cases:
            with self.subTest(case.name, arguments=case.arrangement.as_str):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    args.LineNum2(case.arrangement).as_remaining_source,
                    models.ARBITRARY_MODEL,
                    arrangement_wo_tcds(),
                    Expectation(
                        primitive=prim_asrt__constant(
                            IntervalOfMatcherAssertion(
                                case.expectation,
                            )
                        )
                    ),
                )


class TestContentsPrimitive(unittest.TestCase):
    def runTest(self):
        self._check_cases([
            NArrEx(
                'empty',
                sm_args.Empty(),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'conjunction',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        sm_args.Empty(),
                        sm_args.Equals(FileOrString.of_string('expected')),
                    ])
                ),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'negation',
                arg_rend.within_paren(
                    arg_rend.negation(sm_args.Empty())
                ),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'constant False'
                '(currently not able to derive interval from contents - '
                'would like this to become the empty interval)',
                arg_rend.constant(False),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'constant False',
                arg_rend.constant(True),
                asrt_interval.matches_unlimited()
            ),
        ])

    def _check_cases(self,
                     cases: Sequence[NArrEx[ArgumentElementsRenderer, ValueAssertion[IntIntervalWInversion]]]):
        for case in cases:
            with self.subTest(case.name, arguments=case.arrangement.as_str):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    args.Contents(case.arrangement).as_remaining_source,
                    models.ARBITRARY_MODEL,
                    arrangement_wo_tcds(),
                    Expectation(
                        primitive=prim_asrt__constant(
                            IntervalOfMatcherAssertion(
                                case.expectation,
                            )
                        )
                    ),
                )


class TestConstantPrimitive(unittest.TestCase):
    def runTest(self):
        self._check_cases([
            NArrEx(
                'constant False',
                arg_rend.constant(False),
                asrt_interval.matches_empty()
            ),
            NArrEx(
                'constant True',
                arg_rend.constant(True),
                asrt_interval.matches_unlimited()
            ),
        ])

    def _check_cases(self,
                     cases: Sequence[NArrEx[ArgumentElementsRenderer, ValueAssertion[IntIntervalWInversion]]]):
        for case in cases:
            with self.subTest(case.name, arguments=case.arrangement.as_str):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    case.arrangement.as_remaining_source,
                    models.ARBITRARY_MODEL,
                    arrangement_wo_tcds(),
                    Expectation(
                        primitive=prim_asrt__constant(
                            IntervalOfMatcherAssertion(
                                case.expectation,
                            )
                        )
                    ),
                )


class TestComposition(unittest.TestCase):
    def runTest(self):
        self._check_cases([
            NArrEx(
                '! >= (within line-num-range)',
                arg_rend.negation(
                    args.LineNum2(im_args.comparison2(comparators.GTE, 4))
                ),
                asrt_interval.matches_upper_limit(4 - 1)
            ),
            NArrEx(
                '! >= (outside line-num-range)',
                arg_rend.negation(
                    args.LineNum2(im_args.comparison2(comparators.LTE, FIRST_LINE_NUMBER - 1))
                ),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'negation contents',
                arg_rend.negation(args.Contents(sm_args.Empty())),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'negation constant False',
                arg_rend.negation(arg_rend.constant(False)),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'negation constant True',
                arg_rend.negation(arg_rend.constant(True)),
                asrt_interval.matches_empty()
            ),

            NArrEx(
                '> && <= (within line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        args.LineNum2(im_args.comparison2(comparators.GT, 7)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, 12)),
                    ])
                ),
                asrt_interval.matches_finite(7 + 1, 12)
            ),
            NArrEx(
                '> && contents (within line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        args.LineNum2(im_args.comparison2(comparators.GT, 7)),
                        args.Contents(sm_args.Empty()),
                    ])
                ),
                asrt_interval.matches_lower_limit(7 + 1)
            ),
            NArrEx(
                'contents && contents',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        args.Contents(sm_args.Empty()),
                        args.Contents(sm_args.Empty()),
                    ])
                ),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                '> && <= (partly outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        args.LineNum2(im_args.comparison2(comparators.GT, -7)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, 12)),
                    ])
                ),
                asrt_interval.matches_upper_limit(12)
            ),
            NArrEx(
                '> && <= (completely outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        args.LineNum2(im_args.comparison2(comparators.GT, -7)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, -2)),
                    ])
                ),
                asrt_interval.matches_empty()
            ),
            NArrEx(
                '> && <= && <= (outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.conjunction([
                        args.LineNum2(im_args.comparison2(comparators.GT, -7)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, 12)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, 15)),
                    ])
                ),
                asrt_interval.matches_upper_limit(12)
            ),

            NArrEx(
                '== || <= (within line-num-range)',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.LineNum2(im_args.comparison2(comparators.EQ, 17)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, 10)),
                    ])
                ),
                asrt_interval.matches_upper_limit(17)
            ),
            NArrEx(
                '== || contents (within line-num-range)',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.LineNum2(im_args.comparison2(comparators.EQ, 17)),
                        args.Contents(sm_args.Empty()),
                    ])
                ),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                'contents || contents',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.Contents(sm_args.Empty()),
                        args.Contents(sm_args.Empty()),
                    ])
                ),
                asrt_interval.matches_unlimited()
            ),
            NArrEx(
                '> || == (outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.LineNum2(im_args.comparison2(comparators.GT, 5)),
                        args.LineNum2(im_args.comparison2(comparators.EQ, -12)),
                    ])
                ),
                asrt_interval.matches_lower_limit(5 + 1)
            ),
            NArrEx(
                '< || <= (completely outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.LineNum2(im_args.comparison2(comparators.LT, -5)),
                        args.LineNum2(im_args.comparison2(comparators.LTE, -3)),
                    ])
                ),
                asrt_interval.matches_empty()
            ),
            NArrEx(
                '<= || > || == (outside line-num-range)',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.LineNum2(im_args.comparison2(comparators.LTE, 0)),
                        args.LineNum2(im_args.comparison2(comparators.GT, 5)),
                        args.LineNum2(im_args.comparison2(comparators.EQ, 3)),
                    ])
                ),
                asrt_interval.matches_lower_limit(3)
            ),
            NArrEx(
                '<= || contents || == (within line-num-range)',
                arg_rend.within_paren(
                    arg_rend.disjunction([
                        args.LineNum2(im_args.comparison2(comparators.LTE, 12)),
                        args.Contents(sm_args.Empty()),
                        args.LineNum2(im_args.comparison2(comparators.EQ, 15)),
                    ])
                ),
                asrt_interval.matches_unlimited()
            ),
        ])

    def _check_cases(self,
                     cases: Sequence[NArrEx[ArgumentElementsRenderer, ValueAssertion[IntIntervalWInversion]]]):
        for case in cases:
            with self.subTest(case.name, arguments=case.arrangement.as_str):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    case.arrangement.as_remaining_source,
                    models.ARBITRARY_MODEL,
                    arrangement_wo_tcds(),
                    Expectation(
                        primitive=prim_asrt__constant(
                            IntervalOfMatcherAssertion(
                                case.expectation,
                            )
                        )
                    ),
                )


class IntervalOfMatcherAssertion(ValueAssertionBase[LineMatcher]):
    def __init__(self, expected: ValueAssertion[IntIntervalWInversion]):
        self._expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: LineMatcher,
               message_builder: MessageBuilder):
        # ACT #
        actual = line_nums_interval.interval_of_matcher(value)
        # ASSERT #
        self._expected.apply(put, actual,
                             message_builder.for_sub_component('interval_of_matcher'))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
