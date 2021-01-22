from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment

VALUE_TYPE = TypeVar('VALUE_TYPE')


class ApplicationEnvironmentDependentValue(Generic[VALUE_TYPE], ABC):
    """A value that may depend on :class:`ApplicationEnvironment`"""

    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> VALUE_TYPE:
        pass