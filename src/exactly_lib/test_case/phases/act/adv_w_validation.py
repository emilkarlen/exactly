from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.app_env import ApplicationEnvironment

T = TypeVar('T')


class AdvWValidation(Generic[T], ABC):
    @abstractmethod
    def validate(self) -> Optional[TextRenderer]:
        pass

    @abstractmethod
    def resolve(self, environment: ApplicationEnvironment) -> T:
        pass


def resolve_optional(x: Optional[AdvWValidation[T]],
                     environment: ApplicationEnvironment,
                     ) -> T:
    return (
        None
        if x is None
        else
        x.resolve(environment)
    )
