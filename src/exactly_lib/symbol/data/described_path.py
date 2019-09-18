from abc import ABC, abstractmethod

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.type_system.data.described_path import DescribedPathValue
from exactly_lib.type_system.data.path_describer import PathDescriberForResolver
from exactly_lib.util.symbol_table import SymbolTable


class DescribedPathResolver(ABC):
    """
    A resolver of a FileRef, together with a description,
    and ability to resolve a corresponding object for the resolved value.
    """

    @property
    @abstractmethod
    def resolver(self) -> FileRefResolver:
        pass

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForResolver:
        pass

    @abstractmethod
    def resolve__with_cwd_as_cd(self, symbols: SymbolTable) -> DescribedPathValue:
        pass

    @abstractmethod
    def resolve__with_unknown_cd(self, symbols: SymbolTable) -> DescribedPathValue:
        pass
