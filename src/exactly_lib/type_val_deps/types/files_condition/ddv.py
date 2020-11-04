from abc import ABC

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithDetailsDescriptionDdv
from exactly_lib.type_val_prims.files_condition import FilesCondition

FilesConditionAdv = ApplicationEnvironmentDependentValue[FilesCondition]


class FilesConditionDdv(FullDepsWithDetailsDescriptionDdv[FilesCondition], ABC):
    pass
