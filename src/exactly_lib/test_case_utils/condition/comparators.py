import operator as py_operator_fun
from typing import Any, Callable


class ComparisonOperator(tuple):
    def __new__(cls,
                name: str,
                operator_fun: Callable[[Any, Any], int],
                description: str,
                ):
        return tuple.__new__(cls, (name, operator_fun, description))

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


EQ = ComparisonOperator('==', py_operator_fun.eq, 'equal to')
NE = ComparisonOperator('!=', py_operator_fun.ne, 'not equal to')
LT = ComparisonOperator('<', py_operator_fun.lt, 'less than')
LTE = ComparisonOperator('<=', py_operator_fun.le, 'less than or equal to')
GT = ComparisonOperator('>', py_operator_fun.gt, 'greater than')
GTE = ComparisonOperator('>=', py_operator_fun.ge, 'greater than or equal to')

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
