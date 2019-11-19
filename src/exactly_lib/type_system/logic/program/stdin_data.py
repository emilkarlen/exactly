from typing import Sequence

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.string_or_path_ddvs import StringOrPathDdv, StringOrPath


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


class StdinDataDdv(DirDependentValue[StdinData]):
    def __init__(self, fragments: Sequence[StringOrPathDdv]):
        self._fragments = fragments

    @property
    def fragments(self) -> Sequence[StringOrPathDdv]:
        return self._fragments

    def value_of_any_dependency(self, tcds: Tcds) -> StdinData:
        return StdinData([f.value_of_any_dependency(tcds) for f in self._fragments])
