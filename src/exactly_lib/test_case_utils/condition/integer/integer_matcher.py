from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.type_system.logic.matcher_base_class import Matcher


class IntegerMatcher(Matcher):
    def matches(self, model: int) -> bool:
        raise NotImplementedError('abstract method')


class IntegerMatcherFromComparisonOperator(IntegerMatcher):
    def __init__(self, operator: comparators.ComparisonOperator):
        self._operator = operator
