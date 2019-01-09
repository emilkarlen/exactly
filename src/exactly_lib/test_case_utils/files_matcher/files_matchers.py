from abc import ABC

from exactly_lib.symbol.files_matcher import FilesMatcherResolver
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.logic_types import ExpectationType


class FilesMatcherResolverBase(FilesMatcherResolver, ABC):
    def __init__(self,
                 expectation_type: ExpectationType,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._expectation_type = expectation_type
        self._validator = validator

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator
