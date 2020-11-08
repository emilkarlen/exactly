from abc import ABC

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithNodeDescriptionDdv
from exactly_lib.type_val_prims.string_model import StringModel

StringModelAdv = ApplicationEnvironmentDependentValue[StringModel]


class StringModelDdv(FullDepsWithNodeDescriptionDdv[StringModel], ABC):
    pass
