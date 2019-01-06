from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.files_matcher.new_model import FilesMatcherModel
from exactly_lib.test_case_utils.files_matcher.structure import FilesMatcherResolver, Environment
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util.logic_types import ExpectationType


class Settings:
    def __init__(self, expectation_type: ExpectationType):
        self.expectation_type = expectation_type


class FilesMatcherResolverBase(FilesMatcherResolver, ABC):
    def __init__(self,
                 settings: Settings,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._settings = settings
        self._validator = validator

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    @abstractmethod
    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        pass


class FilesMatcherResolverBaseForNewModel(FilesMatcherResolverBase, ABC):
    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        return self.matches_new(environment,
                                files_source)

    @abstractmethod
    def matches_new(self,
                    environment: Environment,
                    files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        pass
