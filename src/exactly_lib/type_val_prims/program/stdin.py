from typing import Sequence

from exactly_lib.type_val_deps.types.string_or_path.string_or_path_ddvs import StringOrPath


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
