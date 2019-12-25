from typing import Sequence

from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher


def negation(matcher: LineMatcher) -> LineMatcher:
    return combinator_matchers.Negation(matcher)


def conjunction(matchers: Sequence[LineMatcher]) -> LineMatcher:
    return combinator_matchers.Conjunction(matchers)


def disjunction(matchers: Sequence[LineMatcher]) -> LineMatcher:
    return combinator_matchers.Disjunction(matchers)
