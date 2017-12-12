import operator as py_operator_fun
import types


class ComparisonOperator(tuple):
    def __new__(cls,
                name: str,
                operator_fun: types.FunctionType):
        return tuple.__new__(cls, (name, operator_fun))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def operator_fun(self) -> types.FunctionType:
        """A function that takes two arguments and returns an integer à la cmp§"""
        return self[1]


NE = ComparisonOperator('!=', py_operator_fun.ne)
LT = ComparisonOperator('<', py_operator_fun.lt)
LTE = ComparisonOperator('<=', py_operator_fun.le)
EQ = ComparisonOperator('==', py_operator_fun.eq)
GTE = ComparisonOperator('>=', py_operator_fun.ge)
GT = ComparisonOperator('>', py_operator_fun.gt)

ALL_OPERATORS = {
    NE,
    LT,
    LTE,
    EQ,
    GTE,
    GT,
}

NAME_2_OPERATOR = dict([(op.name, op)
                        for op in ALL_OPERATORS])
