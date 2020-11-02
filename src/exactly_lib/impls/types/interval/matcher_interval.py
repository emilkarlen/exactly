import functools
from typing import Sequence, Generic, Callable

from exactly_lib.impls.types.interval.with_interval import WithIntInterval
from exactly_lib.impls.types.matcher.impls import combinator_matchers
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace, MODEL, MatcherStdTypeVisitor
from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib.util.interval.w_inversion import intervals, combinations
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion


def no_adaption(x: IntIntervalWInversion) -> IntIntervalWInversion:
    return x


def interval_of(matcher: MatcherWTrace[MODEL],
                interval_of_unknown_class: IntIntervalWInversion,
                interval_adaption: Callable[[IntIntervalWInversion], IntIntervalWInversion],
                ) -> IntInterval:
    return interval_of__w_inversion(matcher, interval_of_unknown_class, interval_adaption)


def interval_of__w_inversion(matcher: MatcherWTrace[MODEL],
                             interval_of_unknown_class: IntIntervalWInversion,
                             interval_adaption: Callable[[IntIntervalWInversion], IntIntervalWInversion],
                             ) -> IntIntervalWInversion:
    return matcher.accept(_IntervalComputer(interval_of_unknown_class, interval_adaption))


class _IntervalComputer(Generic[MODEL], MatcherStdTypeVisitor[MODEL, IntIntervalWInversion]):
    def __init__(self,
                 interval_of_unknown_class: IntIntervalWInversion,
                 interval_adaption: Callable[[IntIntervalWInversion], IntIntervalWInversion],
                 ):
        self._interval_of_unknown_class = intervals.WithCustomInversion(
            interval_adaption(interval_of_unknown_class),
            interval_adaption(interval_of_unknown_class.inversion),
        )
        self._interval_adaption = interval_adaption
        self._negation_evaluator = _NegationEvaluator(
            self._interval_of_unknown_class,
            self._eval_matcher,
        )

    def _eval_matcher(self, matcher: MatcherWTrace[MODEL]) -> IntIntervalWInversion:
        return matcher.accept(self)

    def visit_constant(self, value: bool) -> IntIntervalWInversion:
        return self._interval_adaption(_CONSTANTS[value])

    def visit_negation(self, operand: MatcherWTrace[MODEL]) -> IntIntervalWInversion:
        return self._interval_adaption(operand.accept(self._negation_evaluator))

    def visit_conjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> IntIntervalWInversion:
        return self._bin_op(combinations.intersection, operands)

    def visit_disjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> IntIntervalWInversion:
        return self._bin_op(combinations.union, operands)

    def visit_non_standard(self, matcher: MatcherWTrace[MODEL]) -> IntIntervalWInversion:
        if isinstance(matcher, WithIntInterval):
            return self._interval_adaption(matcher.interval)
        else:
            return self._interval_of_unknown_class

    def _bin_op(self,
                operator: Callable[[IntIntervalWInversion, IntIntervalWInversion], IntIntervalWInversion],
                operands: Sequence[MatcherWTrace],
                ) -> IntIntervalWInversion:
        unadapted = functools.reduce(operator, [operand.accept(self) for operand in operands])
        return intervals.WithCustomInversion(
            unadapted,
            self._interval_adaption(unadapted.inversion),
        )


class _NegationEvaluator(Generic[MODEL], MatcherStdTypeVisitor[MODEL, IntIntervalWInversion]):
    def __init__(self,
                 interval_of_unknown_class: IntIntervalWInversion,
                 matcher_evaluator: Callable[[MatcherWTrace[MODEL]], IntIntervalWInversion],
                 ):
        self._interval_of_unknown_class = interval_of_unknown_class
        self._matcher_evaluator = matcher_evaluator

    def visit_constant(self, value: bool) -> IntIntervalWInversion:
        return _CONSTANTS[not value]

    def visit_negation(self, operand: MatcherWTrace[MODEL]) -> IntIntervalWInversion:
        return self._matcher_evaluator(operand)

    def visit_conjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> IntIntervalWInversion:
        return self._matcher_evaluator(
            combinator_matchers.Disjunction([
                combinator_matchers.Negation(operand)
                for operand in operands
            ])
        )

    def visit_disjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> IntIntervalWInversion:
        return self._matcher_evaluator(
            combinator_matchers.Conjunction([
                combinator_matchers.Negation(operand)
                for operand in operands
            ])
        )

    def visit_non_standard(self, matcher: MatcherWTrace[MODEL]) -> IntIntervalWInversion:
        if isinstance(matcher, WithIntInterval):
            return matcher.interval.inversion
        else:
            return intervals.WithCustomInversion(
                self._interval_of_unknown_class.inversion,
                self._interval_of_unknown_class,
            )


_CONSTANTS = {
    False: intervals.Empty(),
    True: intervals.Unlimited(),
}
