from abc import ABC
from typing import Optional

from exactly_lib.util.interval.int_interval import IntInterval
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion


class Empty(IntIntervalWInversion):
    @property
    def is_empty(self) -> bool:
        return True

    @property
    def lower(self) -> Optional[int]:
        raise ValueError('empty interval has no lower limit')

    @property
    def upper(self) -> Optional[int]:
        raise ValueError('empty interval has no upper limit')

    @property
    def inversion(self) -> IntIntervalWInversion:
        return unlimited_with_finite_inversion(self)

    def __str__(self) -> str:
        return '<empty>'


class _NonEmptyNonEverythingBase(IntIntervalWInversion, ABC):
    @property
    def is_empty(self) -> bool:
        return False


class UpperLimit(_NonEmptyNonEverythingBase):
    def __init__(self, upper: int):
        self._upper = upper

    @property
    def lower(self) -> Optional[int]:
        return None

    @property
    def upper(self) -> Optional[int]:
        return self._upper

    @property
    def inversion(self) -> IntIntervalWInversion:
        return LowerLimit(self._upper + 1)

    def __str__(self) -> str:
        return ':{}'.format(self._upper)


class LowerLimit(_NonEmptyNonEverythingBase):
    def __init__(self, lower: int):
        self._lower = lower

    @property
    def lower(self) -> Optional[int]:
        return self._lower

    @property
    def upper(self) -> Optional[int]:
        return None

    @property
    def inversion(self) -> IntIntervalWInversion:
        return UpperLimit(self._lower - 1)

    def __str__(self) -> str:
        return '{}:'.format(self._lower)


class Finite(_NonEmptyNonEverythingBase):
    def __init__(self,
                 lower: int,
                 upper: int,
                 ):
        self._lower = lower
        self._upper = upper

    @property
    def lower(self) -> Optional[int]:
        return self._lower

    @property
    def upper(self) -> Optional[int]:
        return self._upper

    @property
    def inversion(self) -> IntIntervalWInversion:
        return unlimited_with_finite_inversion(self)

    def __str__(self) -> str:
        return '{}:{}'.format(self._lower, self._upper)


class Unlimited(_NonEmptyNonEverythingBase):
    @property
    def lower(self) -> Optional[int]:
        return None

    @property
    def upper(self) -> Optional[int]:
        return None

    @property
    def inversion(self) -> IntIntervalWInversion:
        return Empty()

    def __str__(self) -> str:
        return '<unlimited>'


class WithCustomInversion(IntIntervalWInversion):
    def __init__(self,
                 pos: IntInterval,
                 inversion: IntInterval,
                 ):
        self._pos = pos
        self._inversion = inversion

    @property
    def is_empty(self) -> bool:
        return self._pos.is_empty

    @property
    def lower(self) -> Optional[int]:
        return self._pos.lower

    @property
    def upper(self) -> Optional[int]:
        return self._pos.upper

    @property
    def inversion(self) -> IntIntervalWInversion:
        return WithCustomInversion(self._inversion, self._pos)

    def __str__(self) -> str:
        return '<with custom inversion [{}][{}]>'.format(self._pos, self._inversion)


def point(x: int) -> IntIntervalWInversion:
    return Finite(x, x)


def unlimited_with_unlimited_inversion() -> IntIntervalWInversion:
    return WithCustomInversion(Unlimited(), Unlimited())


def unlimited_with_finite_inversion(finite_negation: IntIntervalWInversion) -> IntIntervalWInversion:
    return WithCustomInversion(Unlimited(), finite_negation)
