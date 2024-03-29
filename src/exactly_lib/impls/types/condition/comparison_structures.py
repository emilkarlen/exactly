from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Set

from exactly_lib.symbol.sdv_structure import TypedSymbolDependentValue
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreSds
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

A = TypeVar('A')
T = TypeVar('T')


class OperandDdv(Generic[T], MultiDependenciesDdv[T], ABC):
    @abstractmethod
    def describer(self) -> DetailsRenderer:
        raise NotImplementedError('abstract method')

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> T:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> T:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError('abstract method')


class OperandSdv(Generic[T], TypedSymbolDependentValue[OperandDdv[T]], ABC):
    """Resolves an operand used in a comparison"""

    def validate_pre_sds(self, environment: PathResolvingEnvironmentPreSds):
        """
        Validates by raising exceptions from `return_svh_via_exceptions`
        """
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> OperandDdv[T]:
        raise NotImplementedError('abstract method')
