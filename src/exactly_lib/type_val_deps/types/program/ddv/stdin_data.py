from typing import Sequence

from exactly_lib.impls.types.string_or_path.ddv import StringOrPathDdv
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_prims.program.stdin import StdinData


class StdinDataDdv(DirDependentValue[StdinData]):
    def __init__(self, fragments: Sequence[StringOrPathDdv]):
        self._fragments = fragments

    @property
    def fragments(self) -> Sequence[StringOrPathDdv]:
        return self._fragments

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StdinData:
        return StdinData([f.value_of_any_dependency(tcds) for f in self._fragments])
