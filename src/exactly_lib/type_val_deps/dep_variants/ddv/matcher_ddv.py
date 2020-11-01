from abc import ABC, abstractmethod
from typing import Generic

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.app_env_dep_ddv import LogicWithNodeDescriptionDdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace


class MatcherDdv(Generic[MODEL],
                 LogicWithNodeDescriptionDdv[MatcherWTrace[MODEL]],
                 ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        pass
