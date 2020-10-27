from abc import ABC, abstractmethod
from typing import Optional


class IntInterval(ABC):
    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @property
    @abstractmethod
    def lower(self) -> Optional[int]:
        """
        Precondition: not `is_empty`

        :return: Lower limit (including), or None if unlimited. <= upper
        """
        pass

    @property
    @abstractmethod
    def upper(self) -> Optional[int]:
        """
        Precondition: not `is_empty`

        :return: Upper limit (including), or None if unlimited. >= lower
        """
        pass


class Empty(IntInterval):
    @property
    def is_empty(self) -> bool:
        return True

    @property
    def lower(self) -> Optional[int]:
        raise ValueError('empty interval has no lower limit')

    @property
    def upper(self) -> Optional[int]:
        raise ValueError('empty interval has no upper limit')

    def __str__(self) -> str:
        return '<empty>'


class NonEmpty(IntInterval):
    def __init__(self,
                 lower: Optional[int],
                 upper: Optional[int],
                 ):
        """
        If not None: lower <= upper
        """
        self._lower = lower
        self._upper = upper

    @property
    def is_empty(self) -> bool:
        return False

    @property
    def lower(self) -> Optional[int]:
        return self._lower

    @property
    def upper(self) -> Optional[int]:
        return self._upper

    def __str__(self) -> str:
        return (
            '<unlimited>'
            if self._lower is None and self._upper is None
            else
            '{}:{}'.format(self._lower, self._upper)
        )


def unlimited() -> IntInterval:
    return NonEmpty(None, None)


def lower_limit(lower: int) -> IntInterval:
    return NonEmpty(lower, None)


def upper_limit(upper: int) -> IntInterval:
    return NonEmpty(None, upper)


def finite(lower: int, upper: int) -> IntInterval:
    return NonEmpty(lower, upper)


def point(x: int) -> IntInterval:
    return NonEmpty(x, x)
