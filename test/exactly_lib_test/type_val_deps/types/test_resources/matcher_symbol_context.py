from abc import ABC
from typing import TypeVar, Generic, Optional

from exactly_lib.impls.types.matcher.impls import symbol_reference
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib_test.test_resources import matcher_argument as matcher_args
from exactly_lib_test.test_resources.matcher_argument import MatcherArgument
from exactly_lib_test.type_val_deps.test_resources.full_deps.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext

MODEL = TypeVar('MODEL')


class MatcherSymbolValueContext(Generic[MODEL], LogicSymbolValueContext[MatcherSdv[MODEL]], ABC):
    def __init__(self,
                 sdv: MatcherSdv[MODEL],
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)


class MatcherTypeSymbolContext(Generic[MODEL], LogicTypeSymbolContext[MatcherSdv[MODEL]], ABC):
    def __init__(self,
                 name: str,
                 value: MatcherSymbolValueContext[MODEL],
                 ):
        super().__init__(name)
        self._value = value

    @property
    def value(self) -> MatcherSymbolValueContext[MODEL]:
        return self._value

    @property
    def reference_sdv(self) -> MatcherSdv[MODEL]:
        return symbol_reference.MatcherReferenceSdv(self.name, self.value.value_type)

    @property
    def argument(self) -> MatcherArgument:
        return matcher_args.SymbolReferenceWReferenceSyntax(self.name)
