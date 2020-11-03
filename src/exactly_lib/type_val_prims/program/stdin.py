from typing import Sequence

from exactly_lib.impls.types.string_or_path.primitive import StringOrPath


class StdinData(tuple):
    """
    Text that should become the stdin contents of a process.

    Made up of zero or more fragments that should be concatenated.
    """

    def __new__(cls,
                fragments: Sequence[StringOrPath]):
        return tuple.__new__(cls, (fragments,))

    @property
    def fragments(self) -> Sequence[StringOrPath]:
        return self[0]

    @property
    def is_empty(self) -> bool:
        return len(self.fragments) == 0
