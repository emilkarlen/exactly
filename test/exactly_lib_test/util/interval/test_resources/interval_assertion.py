from typing import Optional, Generic, TypeVar

from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion

T = TypeVar('T')


class PosNeg(Generic[T]):
    def __init__(self,
                 pos: T,
                 neg: T,
                 ):
        self.pos = pos
        self.neg = neg


def equals_interval(expected: IntInterval) -> Assertion[IntInterval]:
    return (
        matches_empty()
        if expected.is_empty
        else
        matches_non_empty(expected.lower, expected.upper)
    )


def matches_non_empty(lower_limit: Optional[int],
                      upper_limit: Optional[int],
                      ) -> Assertion[IntInterval]:
    return asrt.is_instance_with__many(
        IntInterval,
        [
            asrt.sub_component('is_empty',
                               _get_is_empty,
                               asrt.equals(False)
                               ),
            asrt.sub_component('lower',
                               _get_lower,
                               asrt.equals(lower_limit)
                               ),
            asrt.sub_component('upper',
                               _get_upper,
                               asrt.equals(upper_limit)
                               ),
        ]
        ,
    )


def matches_empty() -> Assertion[IntInterval]:
    return asrt.is_instance_with(
        IntInterval,
        asrt.sub_component('is_empty',
                           _get_is_empty,
                           asrt.equals(True)
                           )
    )


def matches_point(n: int) -> Assertion[IntInterval]:
    return matches_non_empty(lower_limit=n, upper_limit=n)


def matches_lower_limit(n: int) -> Assertion[IntInterval]:
    return matches_non_empty(lower_limit=n, upper_limit=None)


def matches_upper_limit(n: int) -> Assertion[IntInterval]:
    return matches_non_empty(lower_limit=None, upper_limit=n)


def matches_finite(m: int, n: int) -> Assertion[IntInterval]:
    return matches_non_empty(lower_limit=m, upper_limit=n)


def matches_unlimited() -> Assertion[IntInterval]:
    return matches_non_empty(lower_limit=None, upper_limit=None)


def is_interval_for_eq(point: int) -> PosNeg[Assertion[IntInterval]]:
    return PosNeg(
        pos=matches_point(point),
        neg=matches_unlimited(),
    )


def is_interval_for_ne(point: int) -> PosNeg[Assertion[IntInterval]]:
    return PosNeg(
        pos=matches_unlimited(),
        neg=matches_point(point),
    )


def is_interval_for_lt(n: int) -> PosNeg[Assertion[IntInterval]]:
    return PosNeg(
        pos=matches_upper_limit(n - 1),
        neg=matches_lower_limit(n),
    )


def is_interval_for_lte(n: int) -> PosNeg[Assertion[IntInterval]]:
    return PosNeg(
        pos=matches_upper_limit(n),
        neg=matches_lower_limit(n + 1),
    )


def is_interval_for_gt(n: int) -> PosNeg[Assertion[IntInterval]]:
    return PosNeg(
        pos=matches_lower_limit(n + 1),
        neg=matches_upper_limit(n),
    )


def is_interval_for_gte(n: int) -> PosNeg[Assertion[IntInterval]]:
    return PosNeg(
        pos=matches_lower_limit(n),
        neg=matches_upper_limit(n - 1),
    )


def _get_is_empty(x: IntInterval) -> bool:
    return x.is_empty


def _get_lower(x: IntInterval) -> Optional[int]:
    return x.lower


def _get_upper(x: IntInterval) -> Optional[int]:
    return x.upper
