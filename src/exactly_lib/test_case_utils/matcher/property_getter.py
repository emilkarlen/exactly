from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar, Optional

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')
T = TypeVar('T')


class PropertyGetter(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def name(self) -> Optional[str]:
        """
        :return: None iff the getter should not be included in the structure / trace -
        it serves as an implementation detail
        """
        pass

    @abstractmethod
    def get_from(self, model: MODEL) -> T:
        """
        :raises HardErrorException
        """
        pass


class PropertyGetterValue(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def name(self) -> Optional[str]:
        """
        :return: None iff the getter should not be included in the structure / trace -
        it serves as an implementation detail
        """
        pass

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> PropertyGetter[MODEL, T]:
        pass

    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()


class PropertyGetterSdv(Generic[MODEL, T], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> PropertyGetterValue[MODEL, T]:
        pass
