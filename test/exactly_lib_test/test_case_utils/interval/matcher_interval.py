import unittest
from typing import Any, Sequence, Callable

from exactly_lib.test_case_utils.interval import matcher_interval as sut
from exactly_lib.test_case_utils.interval.with_interval import WithIntInterval
from exactly_lib.test_case_utils.matcher.impls.combinator_matchers import Negation, Conjunction, Disjunction
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, T, MatcherStdTypeVisitor
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib.util.interval.w_inversion.intervals import point, Empty, UpperLimit, LowerLimit, Finite, \
    Unlimited, \
    unlimited_with_unlimited_inversion
from exactly_lib_test.test_case_utils.matcher.test_resources.matchers import MatcherThatReportsHardError, \
    ConstantMatcherWithCustomName
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.interval.test_resources import interval_assertion as asrt_interval
from exactly_lib_test.util.interval.test_resources.interval_assertion import PosNeg


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestMatcherWInterval(),
        TestMatcherWoInterval(),
        TestConstantWoInterval(),
        TestConstantWInterval(),
        unittest.makeSuite(TestNegation),
        unittest.makeSuite(TestConjunction),
        unittest.makeSuite(TestDisjunction),
    ])


class TestMatcherWInterval(unittest.TestCase):
    def runTest(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=point(72),
            cases=[
                CaseWAdaptionVariants(
                    'point',
                    _MatcherWInterval(point(5)),
                    [
                        _without_adaption(_equals_interval(point(5))),
                        _w_max_upper_adaption(3, _equals_interval(Empty())),
                    ],
                ),
                CaseWAdaptionVariants(
                    'upper limit',
                    _MatcherWInterval(UpperLimit(12)),
                    [
                        _without_adaption(_equals_interval(UpperLimit(12))),
                        _w_max_upper_adaption(10, _equals_interval(UpperLimit(10))),
                    ],
                ),
            ]
        )


class TestMatcherWoInterval(unittest.TestCase):
    def runTest(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=UpperLimit(100),
            cases=[
                CaseWAdaptionVariants(
                    'wo interval',
                    _matcher_wo_interval(),
                    [
                        _without_adaption(_equals_interval(UpperLimit(100))),
                        _w_max_upper_adaption(50, asrt_interval.matches_upper_limit(50)),
                    ]
                ),
            ],
        )


class TestConstantWInterval(unittest.TestCase):
    def runTest(self):
        interval_of_matcher = point(28)
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=point(72),
            cases=[
                CaseWAdaptionVariants(
                    str(False),
                    _ConstantMatcherWInterval(False, interval_of_matcher),
                    [
                        _without_adaption(_equals_interval(Empty())),
                        _w_max_upper_adaption(50, _equals_interval(Empty())),
                    ],
                ),
                CaseWAdaptionVariants(
                    str(True),
                    _ConstantMatcherWInterval(True, interval_of_matcher),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(50, _equals_interval(UpperLimit(50))),
                    ],
                ),
            ]
        )


class TestConstantWoInterval(unittest.TestCase):
    def runTest(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=point(72),
            cases=[
                CaseWAdaptionVariants(
                    str(False),
                    _constant_wo_interval(False),
                    [
                        _without_adaption(_equals_interval(Empty())),
                        _w_max_upper_adaption(50, _equals_interval(Empty())),
                    ],
                ),
                CaseWAdaptionVariants(
                    str(True),
                    _constant_wo_interval(True),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(50, _equals_interval(UpperLimit(50))),
                    ],
                ),
            ]
        )


class TestNegation(unittest.TestCase):
    def test_non_complex(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=unlimited_with_unlimited_inversion(),
            cases=[
                CaseWAdaptionVariants(
                    'constant F',
                    Negation(_constant_wo_interval(False)),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'constant T',
                    Negation(_constant_wo_interval(True)),
                    [
                        _without_adaption(_equals_interval(Empty())),
                        _w_max_upper_adaption(20, _equals_interval(Empty())),
                    ],
                ),
                CaseWAdaptionVariants(
                    'matcher w interval / point',
                    Negation(_MatcherWInterval(point(5))),
                    [
                        _without_adaption(_equals_negation_of(point(5))),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'matcher w interval / upper limit',
                    Negation(_MatcherWInterval(UpperLimit(10))),
                    [
                        _without_adaption(_equals_interval(LowerLimit(10 + 1))),
                        _w_max_upper_adaption(20, _equals_interval(Finite(10 + 1, 20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'matcher wo interval',
                    Negation(_matcher_wo_interval()),
                    [
                        _without_adaption(_equals_interval(unlimited_with_unlimited_inversion())),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
            ]
        )

    def test_double_negation(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=unlimited_with_unlimited_inversion(),
            cases=[
                CaseWAdaptionVariants(
                    'constant F',
                    Negation(Negation(_constant_wo_interval(False))),
                    [
                        _without_adaption(_equals_interval(Empty())),
                        _w_max_upper_adaption(20, _equals_interval(Empty())),
                    ],
                ),
                CaseWAdaptionVariants(
                    'constant T',
                    Negation(Negation(_constant_wo_interval(True))),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'matcher w interval / point',
                    Negation(Negation(_MatcherWInterval(point(5)))),
                    [
                        _without_adaption(_equals_interval(point(5))),
                        _w_max_upper_adaption(0, _equals_interval(Empty())),
                    ],
                ),
                CaseWAdaptionVariants(
                    'matcher w interval / upper limit',
                    Negation(Negation(_MatcherWInterval(UpperLimit(10)))),
                    [
                        _without_adaption(_equals_interval(UpperLimit(10))),
                        _w_max_upper_adaption(5, _equals_interval(UpperLimit(5))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'matcher wo interval',
                    Negation(Negation(_matcher_wo_interval())),
                    [
                        _without_adaption(_equals_interval(unlimited_with_unlimited_inversion())),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'conjunction, all w interval',
                    Negation(
                        Negation(
                            Conjunction([
                                _MatcherWInterval(UpperLimit(10)),
                                _MatcherWInterval(UpperLimit(10 + 5)),
                            ])
                        )
                    ),
                    [
                        _without_adaption(_equals_interval(UpperLimit(10))),
                        _w_max_upper_adaption(5, _equals_interval(UpperLimit(5))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'conjunction, one w unlimited-negation',
                    Negation(
                        Negation(
                            Conjunction([
                                _MatcherWInterval(UpperLimit(10)),
                                _matcher_wo_interval(),
                            ])
                        )
                    ),
                    [
                        _without_adaption(_equals_interval(UpperLimit(10))),
                        _w_max_upper_adaption(5, _equals_interval(UpperLimit(5))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'disjunction, all w interval',
                    Negation(
                        Negation(
                            Disjunction([
                                _MatcherWInterval(UpperLimit(10)),
                                _MatcherWInterval(UpperLimit(10 + 5)),
                            ])
                        )
                    ),
                    [
                        _without_adaption(_equals_interval(UpperLimit(10 + 5))),
                        _w_max_upper_adaption(5, _equals_interval(UpperLimit(5))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'disjunction, one w unlimited-negation',
                    Negation(
                        Negation(
                            Disjunction([
                                _MatcherWInterval(UpperLimit(10)),
                                _matcher_wo_interval(),
                            ])
                        )
                    ),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(5, _equals_interval(UpperLimit(5))),
                    ],
                ),
            ]
        )

    def test_negation_of_conjunction_should_distribute_negation(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=unlimited_with_unlimited_inversion(),
            cases=[
                CaseWAdaptionVariants(
                    'two operands, all w normal negation',
                    Negation(
                        Conjunction([
                            _MatcherWInterval(UpperLimit(10)),
                            _MatcherWInterval(UpperLimit(10 + 5)),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(LowerLimit(10 + 1))),
                        _w_max_upper_adaption(20, _equals_interval(Finite(10 + 1, 20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, one w unlimited-w-unlimited-negation',
                    Negation(
                        Conjunction([
                            _MatcherWInterval(UpperLimit(0)),
                            _matcher_wo_interval(),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'nested negation of conjunction, one w unlimited-w-unlimited-negation',
                    Negation(
                        Conjunction([
                            Negation(
                                Conjunction([
                                    _MatcherWInterval(UpperLimit(0)),
                                    _matcher_wo_interval(),
                                ])),
                            _MatcherWInterval(LowerLimit(10 + 1)),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(UpperLimit(10))),
                        _w_max_upper_adaption(5, _equals_interval(UpperLimit(5))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'nested negation of disjunction, one w unlimited-w-unlimited-negation',
                    Negation(
                        Conjunction([
                            Negation(
                                Disjunction([
                                    _MatcherWInterval(UpperLimit(0)),
                                    _matcher_wo_interval(),
                                ])),
                            _MatcherWInterval(LowerLimit(10 + 1)),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(20, _equals_interval(UpperLimit(20))),
                    ],
                ),
            ]
        )

    def test_negation_of_disjunction_should_distribute_negation(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=unlimited_with_unlimited_inversion(),
            cases=[
                CaseWAdaptionVariants(
                    'two operands, all w normal negation',
                    Negation(
                        Disjunction([
                            _MatcherWInterval(UpperLimit(10)),
                            _MatcherWInterval(UpperLimit(10 + 5)),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(LowerLimit(10 + 5 + 1))),
                        _w_max_upper_adaption(20, _equals_interval(Finite(10 + 5 + 1, 20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, one w unlimited-w-unlimited-negation',
                    Negation(
                        Disjunction([
                            _MatcherWInterval(UpperLimit(0)),
                            _matcher_wo_interval(),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(LowerLimit(0 + 1))),
                        _w_max_upper_adaption(20, _equals_interval(Finite(0 + 1, 20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'nested negation of disjunction, one w unlimited-w-unlimited-negation',
                    Negation(
                        Disjunction([
                            Negation(
                                Disjunction([
                                    _MatcherWInterval(UpperLimit(0)),
                                    _matcher_wo_interval(),
                                ])),
                            _MatcherWInterval(UpperLimit(10 - 1)),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(LowerLimit(10))),
                        _w_max_upper_adaption(20, _equals_interval(Finite(10, 20))),
                    ],
                ),
                CaseWAdaptionVariants(
                    'nested negation of conjunction, one w unlimited-w-unlimited-negation',
                    Negation(
                        Disjunction([
                            Negation(
                                Conjunction([
                                    _MatcherWInterval(UpperLimit(20)),
                                    _matcher_wo_interval(),
                                ])),
                            _MatcherWInterval(UpperLimit(10)),
                        ])
                    ),
                    [
                        _without_adaption(_equals_interval(Finite(10 + 1, 20))),
                        _w_max_upper_adaption(15, _equals_interval(Finite(10 + 1, 15))),
                    ],
                ),
            ]
        )


class TestConjunction(unittest.TestCase):
    def test__unknown_class_is_unlimited_w_unlimited_complement(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=unlimited_with_unlimited_inversion(),
            cases=[
                CaseWAdaptionVariants(
                    'two operands',
                    Conjunction([
                        _MatcherWInterval(Finite(-72, 69 + 5)),
                        _MatcherWInterval(Finite(-72 - 9, 69)),
                    ]),
                    [
                        _without_adaption(_equals_interval(Finite(-72, 69))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-72, 50)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, one wo interval',
                    Conjunction([
                        _MatcherWInterval(Finite(-72, 69)),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(_equals_interval(Finite(-72, 69))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-72, 50)),
                    ]
                ),
                CaseWAdaptionVariants(
                    'two operands, all wo interval',
                    Conjunction([
                        _matcher_wo_interval(),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(50, asrt_interval.matches_upper_limit(50)),
                    ]
                ),
                CaseWAdaptionVariants(
                    'three operands',
                    Conjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _MatcherWInterval(LowerLimit(-11)),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(_equals_interval(LowerLimit(-3))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-3, 50)),
                    ]
                ),
                CaseWAdaptionVariants(
                    'three operands, one wo interval',
                    Conjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _matcher_wo_interval(),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(_equals_interval(LowerLimit(-3))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-3, 50)),
                    ],
                ),
            ]
        )

    def test__unknown_class_is_limited(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=UpperLimit(100),
            cases=[
                CaseWAdaptionVariants(
                    'two operands',
                    Conjunction([
                        _MatcherWInterval(Finite(-72, 69 + 5)),
                        _MatcherWInterval(Finite(-72 - 9, 69)),
                    ]),
                    [
                        _without_adaption(_equals_interval(Finite(-72, 69))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-72, 50)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, one wo interval',
                    Conjunction([
                        _MatcherWInterval(Finite(-70, 200)),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(asrt_interval.matches_finite(-70, 100)),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-70, 50)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, all wo interval',
                    Conjunction([
                        _matcher_wo_interval(),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(asrt_interval.matches_upper_limit(100)),
                        _w_max_upper_adaption(200, asrt_interval.matches_upper_limit(100)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'three operands',
                    Conjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _MatcherWInterval(LowerLimit(-11)),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(_equals_interval(LowerLimit(-3))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-3, 50)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'three operands, one wo interval',
                    Conjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _matcher_wo_interval(),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(_equals_interval(Finite(-3, 100))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-3, 50)),
                    ],
                ),
            ]
        )


class TestDisjunction(unittest.TestCase):
    def test__unknown_class_is_unlimited_w_unlimited_negation(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=unlimited_with_unlimited_inversion(),
            cases=[
                CaseWAdaptionVariants(
                    'two operands',
                    Disjunction([
                        _MatcherWInterval(Finite(-72, 69 + 5)),
                        _MatcherWInterval(Finite(-72 - 9, 69)),
                    ]),
                    [
                        _without_adaption(_equals_interval(Finite(-72 - 9, 69 + 5))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-72 - 9, 50))
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, one wo interval',
                    Disjunction([
                        _MatcherWInterval(Finite(-72, 69 + 5)),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(50, asrt_interval.matches_upper_limit(50))
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, all wo interval',
                    Disjunction([
                        _matcher_wo_interval(),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(50, asrt_interval.matches_upper_limit(50))
                    ],
                ),
                CaseWAdaptionVariants(
                    'three operands',
                    Disjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _MatcherWInterval(LowerLimit(-11)),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(_equals_interval(LowerLimit(-11))),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-11, 50))
                    ],
                ),
                CaseWAdaptionVariants(
                    'three operands, one wo interval',
                    Disjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _matcher_wo_interval(),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(_equals_interval(Unlimited())),
                        _w_max_upper_adaption(50, asrt_interval.matches_upper_limit(50))
                    ],
                ),
            ]
        )

    def test__unknown_class_is_limited_interval(self):
        _check_adaption_variant_cases(
            self,
            interval_of_unknown_class=LowerLimit(-200),
            cases=[
                CaseWAdaptionVariants(
                    'two operands, one wo interval',
                    Disjunction([
                        _MatcherWInterval(Finite(-70, 60)),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(asrt_interval.matches_lower_limit(-200)),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-200, 50)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'two operands, all wo interval',
                    Disjunction([
                        _matcher_wo_interval(),
                        _matcher_wo_interval(),
                    ]),
                    [
                        _without_adaption(asrt_interval.matches_lower_limit(-200)),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-200, 50)),
                    ],
                ),
                CaseWAdaptionVariants(
                    'three operands, one wo interval',
                    Disjunction([
                        _MatcherWInterval(LowerLimit(-3)),
                        _matcher_wo_interval(),
                        _MatcherWInterval(LowerLimit(-7)),
                    ]),
                    [
                        _without_adaption(asrt_interval.matches_lower_limit(-200)),
                        _w_max_upper_adaption(50, asrt_interval.matches_finite(-200, 50)),
                    ],
                ),
            ]
        )


IntervalAdapter = Callable[[IntIntervalWInversion], IntIntervalWInversion]
AssertionOnInterval = ValueAssertion[IntInterval]


class CaseWAdaptionVariants:
    def __init__(self,
                 name: str,
                 matcher: MatcherWTrace,
                 adaption_variants: Sequence[NArrEx[IntervalAdapter, AssertionOnInterval]]
                 ):
        self.name = name
        self.matcher = matcher
        self.adaption_variants = adaption_variants


def _without_adaption(expectation: AssertionOnInterval,
                      ) -> NArrEx[IntervalAdapter, AssertionOnInterval]:
    return NArrEx('wo adaption', _no_interval_adaption, expectation)


def _w_max_upper_adaption(max_upper: int, expectation: ValueAssertion[IntInterval],
                          ) -> NArrEx[IntervalAdapter, ValueAssertion[IntInterval]]:
    return NArrEx('max upper {}'.format(max_upper),
                  _interval_adapter__max_upper(max_upper),
                  expectation)


def _equals_interval(positive: IntInterval) -> ValueAssertion[IntInterval]:
    return asrt_interval.equals_interval(positive)


def _equals_negation_of(positive: IntIntervalWInversion) -> ValueAssertion[IntInterval]:
    return asrt_interval.equals_interval(positive.inversion)


def _check_cases__wo_adaption(
        put: unittest.TestCase,
        interval_of_unknown_class: IntIntervalWInversion,
        cases: Sequence[NArrEx[MatcherWTrace[Any], PosNeg[ValueAssertion[IntInterval]]]],
):
    return _check_cases(put, interval_of_unknown_class, _no_interval_adaption, cases)


def _check_adaption_variant_cases(
        put: unittest.TestCase,
        interval_of_unknown_class: IntIntervalWInversion,
        cases: Sequence[CaseWAdaptionVariants],
):
    for case in cases:
        for adaption_variant in case.adaption_variants:
            with put.subTest(main=case.name, adaption_variant=adaption_variant.name):
                _check(put,
                       interval_of_unknown_class,
                       adaption_variant.arrangement,
                       case.matcher,
                       adaption_variant.expectation,
                       )


def _check_cases(
        put: unittest.TestCase,
        interval_of_unknown_class: IntIntervalWInversion,
        interval_adaption: Callable[[IntIntervalWInversion], IntIntervalWInversion],
        cases: Sequence[NArrEx[MatcherWTrace[Any], ValueAssertion[IntInterval]]],
):
    for case in cases:
        with put.subTest(case.name):
            _check_case(put, interval_of_unknown_class, interval_adaption, case)


def _check_case(
        put: unittest.TestCase,
        interval_of_unknown_class: IntIntervalWInversion,
        interval_adaption: Callable[[IntIntervalWInversion], IntIntervalWInversion],
        case: NArrEx[MatcherWTrace[Any], ValueAssertion[IntInterval]],
):
    _check(put, interval_of_unknown_class, interval_adaption, case.arrangement, case.expectation)


def _check(
        put: unittest.TestCase,
        interval_of_unknown_class: IntIntervalWInversion,
        interval_adaption: Callable[[IntIntervalWInversion], IntIntervalWInversion],
        matcher: MatcherWTrace[Any],
        expectation: ValueAssertion[IntInterval],
):
    # ACT #
    actual = sut.interval_of(matcher, interval_of_unknown_class, interval_adaption)
    # ASSERT #
    expectation.apply_without_message(put, actual)


def _matcher_wo_interval() -> MatcherWTrace[T]:
    return MatcherThatReportsHardError()


def _no_interval_adaption(x: IntIntervalWInversion) -> IntIntervalWInversion:
    return x


def _interval_adapter__const(adapted: IntIntervalWInversion,
                             ) -> Callable[[IntIntervalWInversion], IntIntervalWInversion]:
    def ret_val(x: IntIntervalWInversion) -> IntIntervalWInversion:
        return adapted

    return ret_val


def _interval_adapter__max_upper(max_upper: int,
                                 ) -> Callable[[IntIntervalWInversion], IntIntervalWInversion]:
    def ret_val(x: IntIntervalWInversion) -> IntIntervalWInversion:
        if x.is_empty:
            return x

        if x.lower is None:
            if x.upper is None:
                # both None
                return UpperLimit(max_upper)
            else:
                # lower None, upper not None
                return UpperLimit(min(x.upper, max_upper))
        else:
            if x.upper is None:
                # lower not None, upper None
                return (
                    Empty()
                    if x.lower > max_upper
                    else
                    Finite(x.lower, max_upper)
                )
            else:
                # lower not None, upper not None
                return (
                    Empty()
                    if x.lower > max_upper
                    else
                    Finite(x.lower, min(x.upper, max_upper))
                )

    return ret_val


class _MatcherWInterval(MatcherWTrace[Any], WithIntInterval):
    def __init__(self, interval: IntIntervalWInversion):
        self._interval = interval

    @property
    def name(self) -> str:
        raise NotImplementedError('should not be used')

    def structure(self) -> StructureRenderer:
        raise NotImplementedError('should not be used')

    def matches_w_trace(self, model: Any) -> MatchingResult:
        raise NotImplementedError('should not be used')

    @property
    def interval(self) -> IntIntervalWInversion:
        return self._interval


class _ConstantMatcherWInterval(MatcherWTrace[Any], WithIntInterval):
    def __init__(self,
                 constant_result: bool,
                 interval: IntIntervalWInversion,
                 ):
        self._constant_result = constant_result
        self._interval = interval

    @property
    def name(self) -> str:
        raise NotImplementedError('should not be used')

    def structure(self) -> StructureRenderer:
        raise NotImplementedError('should not be used')

    def matches_w_trace(self, model: Any) -> MatchingResult:
        raise NotImplementedError('should not be used')

    def accept(self, visitor: MatcherStdTypeVisitor[Any, T]) -> T:
        return visitor.visit_constant(self._constant_result)

    @property
    def interval(self) -> IntIntervalWInversion:
        return self._interval


def _constant_wo_interval(value: bool) -> MatcherWTrace:
    return ConstantMatcherWithCustomName('name', value)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
