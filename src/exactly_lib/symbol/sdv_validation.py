from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, Sequence, Optional, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds, PathResolvingEnvironment
from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.symbol_table import SymbolTable


class ValidationStep(Enum):
    PRE_SDS = 1
    POST_SDS = 2


class SdvValidator:
    """
    Validates an object - usually a path - either pre or post creation of SDS.

    Whether validation is done pre or post SDS depends on whether the validated
    object is outside or inside the SDS.
    """

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Optional[TextRenderer]:
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
    def validate_pre_sds_if_applicable(self) -> Optional[TextRenderer]:
        """
        Validates the object if it is expected to exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    @abstractmethod
    def validate_post_sds_if_applicable(self) -> Optional[TextRenderer]:
        """
        Validates the object if it is expected to NOT exist pre-SDS.
        :return: Error message iff validation was applicable and validation failed.
        """
        raise NotImplementedError()

    def validate_pre_or_post_sds(self) -> Optional[TextRenderer]:
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
                 validator: SdvValidator):
        self._environment = environment
        self._validator = validator

    def validate_pre_sds_if_applicable(self) -> Optional[TextRenderer]:
        return self._validator.validate_pre_sds_if_applicable(self._environment)

    def validate_post_sds_if_applicable(self) -> Optional[TextRenderer]:
        return self._validator.validate_post_sds_if_applicable(self._environment)


def all_of(validators: Sequence[SdvValidator]) -> SdvValidator:
    if len(validators) == 0:
        return ConstantSuccessSdvValidator()
    elif len(validators) == 1:
        return validators[0]
    else:
        return AndSdvValidator(validators)


class ConstantSuccessSdvValidator(SdvValidator):
    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return None


class SingleStepSdvValidator(SdvValidator):
    """
    Validator that just applies validation at a single step,
    and ignores the other.
    """

    def __init__(self,
                 step_to_apply: ValidationStep,
                 validator: SdvValidator,
                 ):
        self.step_to_apply = step_to_apply
        self.validator = validator

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        if self.step_to_apply is ValidationStep.PRE_SDS:
            return self.validator.validate_pre_sds_if_applicable(environment)
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        if self.step_to_apply is ValidationStep.POST_SDS:
            return self.validator.validate_post_sds_if_applicable(environment)
        return None


class AndSdvValidator(SdvValidator):
    def __init__(self, validators: Iterable[SdvValidator]):
        self.validators = validators

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        for validator in self.validators:
            result = validator.validate_pre_sds_if_applicable(environment)
            if result is not None:
                return result
        return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        for validator in self.validators:
            result = validator.validate_post_sds_if_applicable(environment)
            if result is not None:
                return result
        return None


class SdvValidatorOfReferredSdvBase(SdvValidator):
    """
    Validates an object using a referred resolvers validator.
    """

    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        return self._referred_validator(environment).validate_pre_sds_if_applicable(environment)

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return self._referred_validator(environment).validate_post_sds_if_applicable(environment)

    def _referred_validator(self, environment: PathResolvingEnvironment) -> SdvValidator:
        raise NotImplementedError('abstract method')


DdvValidatorResolver = Callable[[SymbolTable], DdvValidator]


def validator_resolver_of_constant_success(symbols: SymbolTable) -> DdvValidator:
    return ddv_validation.constant_success_validator()


class SdvValidatorFromDdvValidator(SdvValidator):
    def __init__(self, get_value_validator: DdvValidatorResolver):
        self._get_value_validator = get_value_validator
        self._hds = None

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        return self._get_validator(environment.symbols).validate_pre_sds_if_applicable(environment.hds)

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        tcds = Tcds(self._hds, environment.sds)
        return self._get_validator(environment.symbols).validate_post_sds_if_applicable(tcds)

    def _get_validator(self, symbols: SymbolTable) -> DdvValidator:
        return self._get_value_validator(symbols)
