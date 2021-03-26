from typing import TypeVar, Generic

L = TypeVar('L')
R = TypeVar('R')


class Either(Generic[L, R]):
    @staticmethod
    def of_left(left: L) -> 'Either[L, R]':
        return _Left(left)

    @staticmethod
    def of_right(right: R) -> 'Either[L, R]':
        return _Right(right)

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return False

    def left(self) -> L:
        raise ValueError('This object do not represent a left')

    def right(self) -> R:
        raise ValueError('This object do not represent a right')


T = TypeVar('T')


class Reducer(Generic[L, R, T]):
    def reduce(self, x: Either[L, R]) -> T:
        return (
            self.reduce_left(x.left())
            if x.is_left()
            else
            self.reduce_right(x.right())
        )

    def reduce_left(self, x: L) -> T:
        raise NotImplementedError('abstract method')

    def reduce_right(self, x: R) -> T:
        raise NotImplementedError('abstract method')


class _Left(Generic[L, R], Either[L, R]):
    def __init__(self, left: L):
        self._left = left

    def is_left(self) -> bool:
        return True

    def left(self) -> L:
        return self._left


class _Right(Generic[L, R], Either[L, R]):
    def __init__(self, right: R):
        self._right = right

    def is_right(self) -> bool:
        return True

    def right(self) -> R:
        return self._right
