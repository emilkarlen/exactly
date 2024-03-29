from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import TypedSymbolDependentValue
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.w_validation import ValidatableDdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class FileMaker(ABC):
    @abstractmethod
    def make(self, path: DescribedPath):
        raise NotImplementedError('abstract method')

    def describer(self, file_name: str) -> DetailsRenderer:
        return details.String(file_name)

    def make__translate_hard_error(self, path: DescribedPath) -> Optional[TextRenderer]:
        try:
            self.make(path)
        except HardErrorException as ex:
            return ex.error
        return None


class FileMakerAdv(ApplicationEnvironmentDependentValue[FileMaker], ABC):
    pass


class FileMakerDdv(ValidatableDdv[FileMakerAdv], ABC):
    @abstractmethod
    def describer(self, file_name: str) -> DetailsRenderer:
        raise NotImplementedError('abstract method')


class FileMakerSdv(TypedSymbolDependentValue[FileMakerDdv], ABC):
    pass
