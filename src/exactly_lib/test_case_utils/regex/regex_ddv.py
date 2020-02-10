from abc import ABC, abstractmethod
from typing import Sequence, Set, Pattern

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable


class RegexDdv(MultiDependenciesDdv[Pattern], ABC):
    @abstractmethod
    def describer(self) -> DetailsRenderer:
        pass

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        raise NotImplementedError('abstract method')

    def validator(self) -> DdvValidator:
        raise NotImplementedError('abstract method')

    def value_when_no_dir_dependencies(self) -> Pattern:
        raise NotImplementedError('abstract method')

    def value_of_any_dependency(self, tcds: Tcds) -> Pattern:
        raise NotImplementedError('abstract method')


class RegexSdv:
    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> RegexDdv:
        raise NotImplementedError('abstract method')
