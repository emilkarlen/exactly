from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, Sequence, Optional, Callable

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironment
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.symbol_table import SymbolTable


class ValidationStep(Enum):
    PRE_SDS = 1
    POST_SDS = 2


class PreOrPostSdsValidator:
    """
    Validates an object - usually a path - either pre or post creation of SDS.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Optional[str]:
        """
        Validates the object using either pre- or post- SDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_sds_if_applicable(environment)
        if error_message is not None:
            return error_message
        return self.validate_post_sds_if_applicable(environment)


class PreOrPostSdsValidatorPrimitive(ABC):
    """
    Validates an object - usually a path - either pre or post creation of SDS.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """

    @abstractmethod
    def validate_pre_sds_if_applicable(self) -> Optional[str]:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    @abstractmethod
    def validate_post_sds_if_applicable(self) -> Optional[str]:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self) -> Optional[str]:
        """
        Validates the object using either pre- or post- SDS.
        :return: Error message iff validation failed.
        """
        error_message = self.validate_pre_sds_if_applicable()
        if error_message is not None:
            return error_message
        return self.validate_post_sds_if_applicable()


class FixedPreOrPostSdsValidator(PreOrPostSdsValidatorPrimitive):
    def __init__(self,
                 environment: PathResolvingEnvironmentPreOrPostSds,
                 validator: PreOrPostSdsValidator):
        self._environment = environment
        self._validator = validator

    def validate_pre_sds_if_applicable(self) -> Optional[str]:
        return self._validator.validate_pre_sds_if_applicable(self._environment)

    def validate_post_sds_if_applicable(self) -> Optional[str]:
        return self._validator.validate_post_sds_if_applicable(self._environment)


def all_of(validators: Sequence[PreOrPostSdsValidator]) -> PreOrPostSdsValidator:
    if len(validators) == 0:
        return ConstantSuccessValidator()
    elif len(validators) == 1:
        return validators[0]
    else:
        return AndValidator(validators)


class ConstantSuccessValidator(PreOrPostSdsValidator):
    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
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

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        if self.step_to_apply is ValidationStep.PRE_SDS:
            return self.validator.validate_pre_sds_if_applicable(environment)
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        if self.step_to_apply is ValidationStep.POST_SDS:
            return self.validator.validate_post_sds_if_applicable(environment)
        return None


class AndValidator(PreOrPostSdsValidator):
    def __init__(self,
                 validators: Iterable[PreOrPostSdsValidator]):
        self.validators = validators

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        for validator in self.validators:
            result = validator.validate_pre_sds_if_applicable(environment)
            if result is not None:
                return result
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
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


class ValidatorOfReferredResolverBase(PreOrPostSdsValidator):
    """
    Validates an object using a referred resolvers validator.
    """

    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        return self._referred_validator(environment).validate_pre_sds_if_applicable(environment)

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        return self._referred_validator(environment).validate_post_sds_if_applicable(environment)

    def _referred_validator(self, environment: PathResolvingEnvironment) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')


class PreOrPostSdsValidatorFromValueValidator(PreOrPostSdsValidator):
    def __init__(self, get_value_validator: Callable[[SymbolTable], PreOrPostSdsValueValidator]):
        self._get_value_validator = get_value_validator
        self._value_validator = None
        self._hds = None

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        if self._value_validator is None:
            self._hds = environment.hds
            self._value_validator = self._get_value_validator(environment.symbols)
        return self._value_validator.validate_pre_sds_if_applicable(environment.hds)

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        tcds = HomeAndSds(self._hds, environment.sds)
        return self._value_validator.validate_post_sds_if_applicable(tcds)
