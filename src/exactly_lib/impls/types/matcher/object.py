from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Set

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ObjectDdv(Generic[T], MultiDependenciesDdv[T], ABC):
    """DDV for an arbitrary object"""

    @abstractmethod
    def describer(self) -> DetailsRenderer:
        pass

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.ConstantDdvValidator.new_success()

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> T:
        pass


class ObjectSdv(Generic[T], SymbolDependentValue, ABC):
    """Resolves an arbitrary object"""

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ObjectDdv[T]:
        pass
