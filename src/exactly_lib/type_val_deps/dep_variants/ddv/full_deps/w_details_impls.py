from typing import Generic, Callable

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import PRIMITIVE, FullDepsWithDetailsDescriptionDdv
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class ConstantDdv(Generic[PRIMITIVE], FullDepsWithDetailsDescriptionDdv[PRIMITIVE]):
    def __init__(self, adv: ApplicationEnvironmentDependentValue[PRIMITIVE]):
        self._adv = adv

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        return self._adv


class DdvFromParts(Generic[PRIMITIVE], FullDepsWithDetailsDescriptionDdv[PRIMITIVE]):
    def __init__(self,
                 make_adv: Callable[[TestCaseDs], ApplicationEnvironmentDependentValue[PRIMITIVE]],
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
                 describer: DetailsRenderer = details.empty(),
                 ):
        self._validator = validator
        self._describer = describer
        self._make_adv = make_adv

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    @property
    def describer(self) -> DetailsRenderer:
        return self._describer

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        return self._make_adv(tcds)
