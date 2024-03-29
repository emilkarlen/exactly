from typing import Optional

from exactly_lib.impls.types.files_condition import files_conditions
from exactly_lib.impls.types.files_condition.impl import reference
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesConditionSdv
from exactly_lib_test.impls.types.files_condition.test_resources import arguments_building as args
from exactly_lib_test.impls.types.files_condition.test_resources.arguments_building import FilesConditionArg
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.full_deps.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.types.files_condition.test_resources.abstract_syntax import \
    FilesConditionSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.files_condition.test_resources.references import is_reference_to_files_condition


def arbitrary_sdv() -> FilesConditionSdv:
    return files_conditions.new_empty()


class FilesConditionSymbolValueContext(LogicSymbolValueContext[FilesConditionSdv]):
    def __init__(self,
                 sdv: FilesConditionSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: FilesConditionSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesConditionSymbolValueContext':
        return FilesConditionSymbolValueContext(sdv,
                                                definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'FilesConditionSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_CONDITION

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_files_condition(symbol_name)


class FilesConditionSymbolContext(LogicTypeSymbolContext[FilesConditionSdv]):
    def __init__(self,
                 name: str,
                 value: FilesConditionSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: FilesConditionSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesConditionSymbolContext':
        return FilesConditionSymbolContext(
            name,
            FilesConditionSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'FilesConditionSymbolContext':
        return FilesConditionSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> FilesConditionSymbolValueContext:
        return self._value

    @property
    def reference_sdv(self) -> FilesConditionSdv:
        return reference.ReferenceSdv(self.name)

    @property
    def argument(self) -> FilesConditionArg:
        return args.SymbolReferenceWReferenceSyntax(self.name)

    @property
    def abstract_syntax(self) -> FilesConditionSymbolReferenceAbsStx:
        return FilesConditionSymbolReferenceAbsStx(self.name)


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesConditionSymbolValueContext.of_sdv(arbitrary_sdv())
