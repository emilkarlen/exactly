from typing import Sequence

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentPrimeValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.string_or_file_ref_values import StringOrFileRefValue, StringOrPath


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


class StdinDataValue(DirDependentPrimeValue[StdinData]):
    def __init__(self, fragments: Sequence[StringOrFileRefValue]):
        self._fragments = fragments

    @property
    def fragments(self) -> Sequence[StringOrFileRefValue]:
        return self._fragments

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StdinData:
        return StdinData([f.value_of_any_dependency(home_and_sds) for f in self._fragments])
