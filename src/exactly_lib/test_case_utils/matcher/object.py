from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Set

from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
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
        return ddv_validation.constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> T:
        pass


class ObjectSdv(Generic[T], SymbolDependentValue, ABC):
    """Resolves an arbitrary object"""

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ObjectDdv[T]:
        pass
