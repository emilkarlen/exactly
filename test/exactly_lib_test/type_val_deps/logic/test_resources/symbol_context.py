from abc import ABC, abstractmethod
from typing import Generic, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib_test.symbol.test_resources.symbol_context import SDV_TYPE, SymbolValueContext, SymbolContext


class LogicSymbolValueContext(Generic[SDV_TYPE], SymbolValueContext[SDV_TYPE], ABC):
    def __init__(self,
                 sdv: SDV_TYPE,
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)


class LogicTypeSymbolContext(Generic[SDV_TYPE], SymbolContext[SDV_TYPE], ABC):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    @abstractmethod
    def value(self) -> LogicSymbolValueContext[SDV_TYPE]:
        pass

    @property
    @abstractmethod
    def reference_sdv(self) -> SDV_TYPE:
        pass
