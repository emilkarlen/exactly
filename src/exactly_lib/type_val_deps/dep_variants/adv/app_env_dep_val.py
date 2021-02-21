from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from exactly_lib.test_case.app_env import ApplicationEnvironment

VALUE_TYPE = TypeVar('VALUE_TYPE')


class ApplicationEnvironmentDependentValue(Generic[VALUE_TYPE], ABC):
    """A value that may depend on :class:`ApplicationEnvironment`"""

    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> VALUE_TYPE:
        pass

    @staticmethod
    def primitive__optional(adv: Optional['ApplicationEnvironmentDependentValue[VALUE_TYPE]'],
                            environment: ApplicationEnvironment,
                            ) -> Optional[VALUE_TYPE]:
        return (
            None
            if adv is None
            else
            adv.primitive(environment)
        )
