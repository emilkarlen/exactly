from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils import svh_exception


class SvhValidatorViaReturnValues:
    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class SvhPreSdsValidatorViaExceptions:
    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        :raises SvhException: Validation fails
        """
        pass


class SvhPostSetupValidatorViaExceptions:
    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds):
        """
        :raises SvhException: Validation fails
        """
        pass


class SvhValidatorViaExceptions(SvhPreSdsValidatorViaExceptions,
                                SvhPostSetupValidatorViaExceptions):
    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        :raises SvhException: Validation fails
        """
        pass

    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds):
        """
        :raises SvhException: Validation fails
        """
        pass


class SvhValidatorViaExceptionsFromPreAndPostSdsValidators(SvhValidatorViaExceptions):
    def __init__(self,
                 pre_sds: SvhPreSdsValidatorViaExceptions = None,
                 post_setup: SvhPostSetupValidatorViaExceptions = None,
                 ):
        self._pre_sds = pre_sds
        self._post_setup = post_setup

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        if self._pre_sds:
            self._pre_sds.validate_pre_sds(environment)

    def validate_post_setup(self, environment: PathResolvingEnvironmentPostSds):
        if self._post_setup:
            self._post_setup.validate_post_setup(environment)


class SdvValidatorFromSdvValidatorViaExceptions(SdvValidator):
    def __init__(self, adapted: SvhValidatorViaExceptions):
        self._adapted = adapted

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        try:
            self._adapted.validate_pre_sds(environment)
        except svh_exception.SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        try:
            self._adapted.validate_post_setup(environment)
        except svh_exception.SvhException as ex:
            return ex.err_msg


class SvhValidatorViaReturnValuesFromValidatorViaExceptions(SvhValidatorViaReturnValues):
    def __init__(self, adapted: SvhValidatorViaExceptions):
        self._adapted = adapted

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> svh.SuccessOrValidationErrorOrHardError:
        return svh_exception.translate_svh_exception_to_svh(self._adapted.validate_pre_sds, environment)

    def validate_post_setup(self,
                            environment: PathResolvingEnvironmentPostSds) -> svh.SuccessOrValidationErrorOrHardError:
        return svh_exception.translate_svh_exception_to_svh(self._adapted.validate_post_setup, environment)


class PreOrPostSdsSvhValidationErrorValidator:
    """
    A validator that translates error messages to a :class:`svh.SuccessOrValidationErrorOrHardError`
    """

    def __init__(self, validator: SdvValidator):
        self.validator = validator

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds
                                       ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_pre_sds_if_applicable(environment))

    def validate_post_sds_if_applicable(self,
                                        environment: PathResolvingEnvironmentPostSds
                                        ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_post_sds_if_applicable(environment))

    def validate_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds
                                 ) -> svh.SuccessOrValidationErrorOrHardError:
        return self._translate(self.validator.validate_pre_or_post_sds(environment))

    @staticmethod
    def _translate(error_message_or_none: Optional[TextRenderer]) -> svh.SuccessOrValidationErrorOrHardError:
        if error_message_or_none is not None:
            return svh.new_svh_validation_error(error_message_or_none)
        return svh.new_svh_success()
