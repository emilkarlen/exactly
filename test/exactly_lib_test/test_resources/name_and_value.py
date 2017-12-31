from typing import Generic, TypeVar

T = TypeVar('T')


class NameAndValue(tuple, Generic[T]):
    """
    A name with an associated value.

    Is a tuple with two elements - so objects can be used wherever pairs can be used.
    """

    def __new__(cls,
                name,
                value: T):
        return tuple.__new__(cls, (name, value))

    @property
    def name(self):
        return self[0]

    @property
    def value(self) -> T:
        return self[1]
