from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.full_deps.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.types.files_source.test_resources import primitives, sdvs
from exactly_lib_test.type_val_deps.types.files_source.test_resources import references
from exactly_lib_test.type_val_deps.types.files_source.test_resources.abstract_syntax import \
    FilesSourceSymbolReferenceAbsStx


class FilesSourceSymbolValueContext(LogicSymbolValueContext[FilesSource]):
    def __init__(self,
                 sdv: FilesSourceSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: FilesSourceSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesSourceSymbolValueContext':
        return FilesSourceSymbolValueContext(sdv, definition_source)

    @staticmethod
    def of_primitive(primitive: FilesSource,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FilesSourceSymbolValueContext':
        return FilesSourceSymbolValueContext(sdvs.FilesSourceSdvConstantPrimitiveTestImpl(primitive), definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'FilesSourceSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_SOURCE

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return references.is_reference_to__files_source(symbol_name)


class FilesSourceSymbolContext(LogicTypeSymbolContext[FilesSource]):
    def __init__(self,
                 name: str,
                 value: FilesSourceSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: FilesSourceSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesSourceSymbolContext':
        return FilesSourceSymbolContext(
            name,
            FilesSourceSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: FilesSource,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FilesSourceSymbolContext':
        return FilesSourceSymbolContext(
            name,
            FilesSourceSymbolValueContext.of_primitive(primitive,
                                                       definition_source),
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'FilesSourceSymbolContext':
        return FilesSourceSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> LogicSymbolValueContext[FilesSourceSdv]:
        return self._value

    @property
    def abstract_syntax(self) -> FilesSourceSymbolReferenceAbsStx:
        return FilesSourceSymbolReferenceAbsStx(self.name)

    @property
    def reference_sdv(self) -> FilesSourceSdv:
        raise ValueType('unsupported - would like to remove this method from base class')
        # since implies too many dependencies


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesSourceSymbolValueContext.of_primitive(
    primitives.FilesSourceThatDoesNothingTestImpl()
)
