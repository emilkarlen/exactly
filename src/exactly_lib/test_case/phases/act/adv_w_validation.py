from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.app_env import ApplicationEnvironment

T = TypeVar('T')


class AdvWValidation(Generic[T], ABC):
    @abstractmethod
    def validate(self) -> Optional[TextRenderer]:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def resolve(self, environment: ApplicationEnvironment) -> T:
        raise NotImplementedError('abstract method')


def resolve_optional(x: Optional[AdvWValidation[T]],
                     environment: ApplicationEnvironment,
                     ) -> T:
    return (
        None
        if x is None
        else
        x.resolve(environment)
    )
