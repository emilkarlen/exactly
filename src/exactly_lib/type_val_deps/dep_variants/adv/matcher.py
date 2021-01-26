from abc import ABC, abstractmethod
from typing import Generic

from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace


class MatcherAdv(Generic[MODEL],
                 ApplicationEnvironmentDependentValue[MatcherWTrace[MODEL]],
                 ABC):
    """Application Environment Dependent Matcher"""

    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        pass
