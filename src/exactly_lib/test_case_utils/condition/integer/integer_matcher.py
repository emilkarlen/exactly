from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.type_system.logic.matcher_base_class import Matcher


class IntegerMatcher(Matcher[int]):
    def matches(self, model: int) -> bool:
        raise NotImplementedError('abstract method')


class IntegerMatcherFromComparisonOperator(IntegerMatcher):
    """Matches on an integer, that serves as the left hand side in a comparison with a constant."""

    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 constant_rhs: int):
        self._constant_rhs = constant_rhs
        self._operator = operator

    @property
    def name(self) -> str:
        return self._operator.name

    def matches(self, model: int) -> bool:
        return self._operator.operator_fun(model, self._constant_rhs)

    @property
    def option_description(self) -> str:
        return ' '.join([self._operator.name,
                         str(self._constant_rhs)])
