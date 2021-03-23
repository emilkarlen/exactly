from abc import ABC

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithDetailsDescriptionDdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource


class FilesSourceAdv(ApplicationEnvironmentDependentValue[FilesSource], ABC):
    pass


class FilesSourceDdv(FullDepsWithDetailsDescriptionDdv[FilesSource], ABC):
    pass
