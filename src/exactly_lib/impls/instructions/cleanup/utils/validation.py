from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case.result import sh
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator


class PreOrPostSdsSvhValidationForSuccessOrHardError:
    """
    A validator that translates error messages to a sh.HardError
    """

    def __init__(self, validator: SdvValidator):
        self.validator = validator

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_sds_if_applicable(environment))

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_post_sds_if_applicable(environment))

    @staticmethod
    def _translate(error_message_or_none: Optional[TextRenderer]) -> sh.SuccessOrHardError:
        if error_message_or_none is not None:
            return sh.new_sh_hard_error(error_message_or_none)
        return sh.new_sh_success()
