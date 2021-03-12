from abc import ABC, abstractmethod

from exactly_lib.symbol.sdv_structure import TypesSymbolDependentValue
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.w_validation import ValidatableDdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class FileMaker(ABC):
    @abstractmethod
    def make(self, path: DescribedPath):
        pass

    def describer(self, file_name: str) -> DetailsRenderer:
        return details.String(file_name)


class FileMakerAdv(ApplicationEnvironmentDependentValue[FileMaker], ABC):
    pass


class FileMakerDdv(ValidatableDdv[FileMakerAdv], ABC):
    @abstractmethod
    def describer(self, file_name: str) -> DetailsRenderer:
        pass


class FileMakerSdv(TypesSymbolDependentValue[FileMakerDdv], ABC):
    pass
