from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Set, Sequence

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ObjectValue(Generic[T], MultiDirDependentValue[T], ABC):
    """Value for an arbitrary object"""

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> T:
        pass


class ObjectResolver(Generic[T], ABC):
    """Resolves an arbitrary object"""

    def __init__(self, property_name: str):
        self.property_name = property_name

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    @property
    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ObjectValue[T]:
        pass
