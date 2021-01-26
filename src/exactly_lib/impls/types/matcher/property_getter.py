from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_prims.description.tree_structured import WithNodeDescription
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')
T = TypeVar('T')


class PropertyGetter(Generic[MODEL, T], WithNodeDescription, ABC):
    @abstractmethod
    def get_from(self, model: MODEL) -> T:
        """
        :raises HardErrorException
        """
        pass


class PropertyGetterAdv(Generic[MODEL, T], ABC):
    @abstractmethod
    def applier(self, environment: ApplicationEnvironment) -> PropertyGetter[MODEL, T]:
        pass


class PropertyGetterDdv(Generic[MODEL, T], WithNodeDescription, ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.ConstantDdvValidator.new_success()

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> PropertyGetterAdv[MODEL, T]:
        pass


class PropertyGetterSdv(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> PropertyGetterDdv[MODEL, T]:
        pass
