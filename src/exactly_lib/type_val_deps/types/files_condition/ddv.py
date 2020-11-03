from abc import ABC

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.chains.described_dep_val import LogicWithDetailsDescriptionDdv
from exactly_lib.type_val_prims.files_condition import FilesCondition

FilesConditionAdv = ApplicationEnvironmentDependentValue[FilesCondition]


class FilesConditionDdv(LogicWithDetailsDescriptionDdv[FilesCondition], ABC):
    pass
