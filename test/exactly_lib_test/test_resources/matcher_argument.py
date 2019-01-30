from abc import ABC, abstractmethod
from typing import List

from exactly_lib.definitions import expression


class MatcherArg(ABC):
    """Generate source using __str__"""
    pass

    def __str__(self):
        return ' '.join([str(element) for element in self.elements])

    @property
    @abstractmethod
    def elements(self) -> List:
        pass


def value_error_if_empty(operator_name: str,
                         matchers: List[MatcherArg]):
    if len(matchers) == 0:
        raise ValueError(operator_name +
                         ' must have at least one matcher')


def value_error_if_empty__and(matchers: List[MatcherArg]):
    value_error_if_empty(expression.AND_OPERATOR_NAME,
                         matchers)


def value_error_if_empty__or(matchers: List[MatcherArg]):
    value_error_if_empty(expression.OR_OPERATOR_NAME,
                         matchers)


def concat_and_intersperse_non_empty_list(operator_name: str,
                                          matchers: List[MatcherArg]) -> List:
    ret_val = matchers[0].elements
    for matcher in matchers[1:]:
        ret_val.append(operator_name)
        ret_val += matcher.elements
    return ret_val
