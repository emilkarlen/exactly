from typing import Optional, List

from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib.util.interval.w_inversion.intervals import Empty, Unlimited, UpperLimit, LowerLimit, Finite


def union(a: IntIntervalWInversion, b: IntIntervalWInversion) -> IntIntervalWInversion:
    if a.is_empty:
        return b
    if b.is_empty:
        return a

    non_none_lowers = _not_nones(a.lower, b.lower)
    non_none_uppers = _not_nones(a.upper, b.upper)

    lower = (
        None
        if len(non_none_lowers) != 2
        else
        min(non_none_lowers)
    )
    upper = (
        None
        if len(non_none_uppers) != 2
        else
        max(non_none_uppers)
    )

    return _of(lower, upper)


def intersection(a: IntIntervalWInversion, b: IntIntervalWInversion) -> IntIntervalWInversion:
    if a.is_empty:
        return a
    if b.is_empty:
        return b

    non_none_lowers = _not_nones(a.lower, b.lower)
    lower = (
        None
        if not non_none_lowers
        else
        max(non_none_lowers)
    )

    non_none_uppers = _not_nones(a.upper, b.upper)
    upper = (
        None
        if not non_none_uppers
        else
        min(non_none_uppers)
    )

    return (
        Empty()
        if lower is not None and upper is not None and lower > upper
        else
        _of(lower, upper)
    )


def _not_nones(x: Optional[int], y: Optional[int]) -> List[int]:
    ret_val = []

    if x is not None:
        ret_val.append(x)
    if y is not None:
        ret_val.append(y)

    return ret_val


def _of(lower: Optional[int], upper: Optional[int]) -> IntIntervalWInversion:
    """
    lower < upper, if both are not None
    """
    if lower is None:
        if upper is None:
            return Unlimited()
        else:
            return UpperLimit(upper)
    else:
        if upper is None:
            return LowerLimit(lower)
        else:
            return Finite(lower, upper)
