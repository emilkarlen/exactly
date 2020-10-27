import operator as py_operator_fun
from typing import Any, Callable

from exactly_lib.util.interval.w_inversion import intervals
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion


class ComparisonOperator(tuple):
    def __new__(cls,
                name: str,
                operator_fun: Callable[[Any, Any], int],
                description: str,
                int_interval: Callable[[int], IntIntervalWInversion],
                ):
        return tuple.__new__(cls, (name, operator_fun, description, int_interval))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def operator_fun(self) -> Callable[[Any, Any], int]:
        """
        :returns An integer à la cmp
        """
        return self[1]

    @property
    def description(self) -> str:
        return self[2]

    def int_interval(self, rhs: int) -> IntIntervalWInversion:
        return self[3](rhs)


def _int_interval_of_ne(x: int) -> IntIntervalWInversion:
    return intervals.unlimited_with_finite_inversion(intervals.point(x))


def _int_interval_of_lt(x: int) -> IntIntervalWInversion:
    return intervals.UpperLimit(x - 1)


def _int_interval_of_gt(x: int) -> IntIntervalWInversion:
    return intervals.LowerLimit(x + 1)


EQ = ComparisonOperator('==', py_operator_fun.eq, 'equal to', intervals.point)
NE = ComparisonOperator('!=', py_operator_fun.ne, 'not equal to', _int_interval_of_ne)
LT = ComparisonOperator('<', py_operator_fun.lt, 'less than', _int_interval_of_lt)
LTE = ComparisonOperator('<=', py_operator_fun.le, 'less than or equal to', intervals.UpperLimit)
GT = ComparisonOperator('>', py_operator_fun.gt, 'greater than', _int_interval_of_gt)
GTE = ComparisonOperator('>=', py_operator_fun.ge, 'greater than or equal to', intervals.LowerLimit)

ALL_OPERATORS = (
    EQ,
    NE,
    LT,
    LTE,
    GT,
    GTE,
)

NAME_2_OPERATOR = dict([(op.name, op)
                        for op in ALL_OPERATORS])
