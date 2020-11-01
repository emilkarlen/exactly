from abc import ABC

from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.app_env_dep_ddv import LogicWithNodeDescriptionDdv

StringTransformerAdv = ApplicationEnvironmentDependentValue[StringTransformer]


class StringTransformerDdv(LogicWithNodeDescriptionDdv[StringTransformer], ABC):
    pass
