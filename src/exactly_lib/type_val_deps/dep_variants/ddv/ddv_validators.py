from typing import Sequence, Iterable, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator, ConstantDdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import PreOrPostSdsValidatorPrimitive


def all_of(validators: Sequence[DdvValidator]) -> DdvValidator:
    if len(validators) == 0:
        return ConstantDdvValidator.new_success()
    elif len(validators) == 1:
        return validators[0]
    else:
        return AndValidator(validators)


class AndValidator(DdvValidator):
    def __init__(self,
                 validators: Iterable[DdvValidator]):
        self.validators = validators

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        for validator in self.validators:
            result = validator.validate_pre_sds_if_applicable(hds)
            if result is not None:
                return result
        return None

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        for validator in self.validators:
            result = validator.validate_post_sds_if_applicable(tcds)
            if result is not None:
                return result
        return None


class FixedPreOrPostSdsValidator(PreOrPostSdsValidatorPrimitive):
    def __init__(self,
                 tcds: TestCaseDs,
                 validator: DdvValidator):
        self._tcds = tcds
        self._validator = validator

    def validate_pre_sds_if_applicable(self) -> Optional[TextRenderer]:
        return self._validator.validate_pre_sds_if_applicable(self._tcds.hds)

    def validate_post_sds_if_applicable(self) -> Optional[TextRenderer]:
        return self._validator.validate_post_sds_if_applicable(self._tcds)
