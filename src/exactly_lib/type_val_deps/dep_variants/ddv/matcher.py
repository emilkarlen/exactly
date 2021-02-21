from abc import ABC, abstractmethod
from typing import Generic, Optional

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithNodeDescriptionDdv
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace


class MatcherDdv(Generic[MODEL],
                 FullDepsWithNodeDescriptionDdv[MatcherWTrace[MODEL]],
                 ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.ConstantDdvValidator.new_success()

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        pass

    @staticmethod
    def value_of_any_dependency__optional(ddv: Optional['MatcherDdv[MODEL]'],
                                          tcds: TestCaseDs) -> Optional[MatcherAdv[MODEL]]:
        return (
            None
            if ddv is None
            else
            ddv.value_of_any_dependency(tcds)
        )
