from typing import Generic, Optional, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation, T

ValidatorFunction = Callable[[], Optional[TextRenderer]]


class ConstantAdvWValidation(Generic[T], AdvWValidation[T]):
    def __init__(self,
                 constant: T,
                 validator: ValidatorFunction,
                 ):
        self._constant = constant
        self._validator = validator

    @staticmethod
    def new_wo_validation(constant: T) -> AdvWValidation[T]:
        return ConstantAdvWValidation(
            constant,
            unconditionally_successful_validator,
        )

    def validate(self) -> Optional[TextRenderer]:
        return self._validator()

    def resolve(self, environment: ApplicationEnvironment) -> T:
        return self._constant


def unconditionally_successful_validator() -> Optional[TextRenderer]:
    return None
