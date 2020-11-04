from abc import ABC

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithNodeDescriptionDdv
from exactly_lib.type_val_prims.string_transformer import StringTransformer

StringTransformerAdv = ApplicationEnvironmentDependentValue[StringTransformer]


class StringTransformerDdv(FullDepsWithNodeDescriptionDdv[StringTransformer], ABC):
    pass
