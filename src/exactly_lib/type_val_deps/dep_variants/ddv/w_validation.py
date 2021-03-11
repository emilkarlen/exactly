from abc import ABC
from typing import Generic, Optional

from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue, RESOLVED_TYPE


class ValidatableDdv(Generic[RESOLVED_TYPE], DirDependentValue[RESOLVED_TYPE], ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.ConstantDdvValidator.new_success()

    @staticmethod
    def validator__optional(ddv: 'Optional[ValidatableDdv[RESOLVED_TYPE]]') -> DdvValidator:
        return (
            ddv_validation.ConstantDdvValidator.new_success()
            if ddv is None
            else
            ddv.validator
        )
