from typing import List

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.test_case_file_structure.dir_dependent_value import DependenciesAwareDdv
from exactly_lib.util.symbol_table import SymbolTable


class DataTypeSdv(SymbolDependentValue):
    """ Base class for symbol values - values that represent data."""

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> DependenciesAwareDdv:
        """
        Resolves the value given a symbol table.
        :rtype: Depends on the concrete value.
        """
        raise NotImplementedError('abstract method')

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds):
        """
        Short cut for resolving the value_of_any_dependency
        """
        return self.resolve(environment.symbols).value_of_any_dependency(environment.tcds)
