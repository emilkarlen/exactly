from typing import Optional

from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import Matcher, MODEL


class ComparisonMatcherForEquivalenceChecks(Matcher[int]):

    def __init__(self,
                 name: str,
                 operator: comparators.ComparisonOperator,
                 constant_rhs: int):
        self._name = name
        self._constant_rhs = constant_rhs
        self._operator = operator

    @property
    def name(self) -> str:
        return self._name

    def matches(self, model: int) -> bool:
        return self._operator.operator_fun(model, self._constant_rhs)

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('unsupported')

    @property
    def option_description(self) -> str:
        raise NotImplementedError('unsupported')
