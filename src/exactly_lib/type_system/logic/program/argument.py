from typing import List, Sequence

from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.list_ddv import ListDdv


class ArgumentsDdv(DirDependentValue[List[str]]):
    def __init__(self,
                 arguments: ListDdv,
                 validators: Sequence[DdvValidator] = ()):
        self._arguments = arguments
        self._validators = validators

    @property
    def arguments_list(self) -> ListDdv:
        return self._arguments

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    def value_of_any_dependency(self, tcds: Tcds) -> List[str]:
        return self._arguments.value_of_any_dependency(tcds)
