from enum import Enum

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh


class ValidationStep(Enum):
    PRE_SDS = 1
    POST_SDS = 2


class PreOrPostSdsValidator:
    """
    Validates an object - usually a path - either pre or post creation of SDS.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        """
        Validates the object using either pre- or post- SDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_sds_if_applicable(environment)
        if error_message is not None:
            return error_message
        return self.validate_post_sds_if_applicable(environment)


class ConstantSuccessValidator(PreOrPostSdsValidator):
    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        return None


class SingleStepValidator(PreOrPostSdsValidator):
    """
    Validator that just applies validation at a single step,
    and ignores the other.
    """

    def __init__(self,
                 step_to_apply: ValidationStep,
                 validator: PreOrPostSdsValidator):
        self.step_to_apply = step_to_apply
        self.validator = validator

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        if self.step_to_apply is ValidationStep.PRE_SDS:
            return self.validator.validate_pre_sds_if_applicable(environment)
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        if self.step_to_apply is ValidationStep.POST_SDS:
            return self.validator.validate_post_sds_if_applicable(environment)
        return None


class AndValidator(PreOrPostSdsValidator):
    def __init__(self,
                 validators: iter):
        self.validators = validators

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        for validator in self.validators:
            result = validator.validate_pre_sds_if_applicable(environment)
            if result is not None:
                return result
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        for validator in self.validators:
            result = validator.validate_post_sds_if_applicable(environment)
            if result is not None:
                return result
        return None


class PreOrPostSdsSvhValidationErrorValidator:
    """
    A validator that translates error messages to a svh.ValidationError
    """

    def __init__(self,
                 validator: PreOrPostSdsValidator):
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
    def _translate(error_message_or_none: str) -> svh.SuccessOrValidationErrorOrHardError:
        if error_message_or_none is not None:
            return svh.new_svh_validation_error(error_message_or_none)
        return svh.new_svh_success()


class PreOrPostSdsSvhValidationForSuccessOrHardError:
    """
    A validator that translates error messages to a sh.HardError
    """

    def __init__(self, validator: PreOrPostSdsValidator):
        self.validator = validator

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_sds_if_applicable(environment))

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_post_sds_if_applicable(environment))

    def validate_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> sh.SuccessOrHardError:
        return self._translate(self.validator.validate_pre_or_post_sds(environment))

    @staticmethod
    def _translate(error_message_or_none: str) -> sh.SuccessOrHardError:
        if error_message_or_none is not None:
            return sh.new_sh_hard_error(error_message_or_none)
        return sh.new_sh_success()
