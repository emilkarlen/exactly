from typing import Optional

from exactly_lib.impls.types.string_transformer import sdvs
from exactly_lib.impls.types.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.logic.test_resources.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer


class StringTransformerSymbolValueContext(LogicSymbolValueContext[StringTransformerSdv]):
    def __init__(self,
                 sdv: StringTransformerSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: StringTransformerSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringTransformerSymbolValueContext':
        return StringTransformerSymbolValueContext(sdv,
                                                   definition_source)

    @staticmethod
    def of_primitive(primitive: StringTransformer,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'StringTransformerSymbolValueContext':
        return StringTransformerSymbolValueContext.of_sdv(sdvs.StringTransformerSdvConstant(primitive),
                                                          definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'StringTransformerSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_TRANSFORMER

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_string_transformer(symbol_name)


class StringTransformerSymbolContext(LogicTypeSymbolContext[StringTransformerSdv]):
    def __init__(self,
                 name: str,
                 value: StringTransformerSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: StringTransformerSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringTransformerSymbolContext':
        return StringTransformerSymbolContext(
            name,
            StringTransformerSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: StringTransformer,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'StringTransformerSymbolContext':
        return StringTransformerSymbolContext(
            name,
            StringTransformerSymbolValueContext.of_primitive(primitive, definition_source)
        )

    @staticmethod
    def of_identity(name: str,
                    definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                    ) -> 'StringTransformerSymbolContext':
        return StringTransformerSymbolContext.of_primitive(name,
                                                           IdentityStringTransformer(),
                                                           definition_source)

    @staticmethod
    def of_arbitrary_value(name: str) -> 'StringTransformerSymbolContext':
        return StringTransformerSymbolContext(
            name,
            ARBITRARY_SYMBOL_VALUE_CONTEXT
        )

    @property
    def reference_sdv(self) -> StringTransformerSdv:
        return sdvs.StringTransformerSdvReference(self.name)

    @property
    def value(self) -> StringTransformerSymbolValueContext:
        return self._value

    @property
    def abstract_syntax(self) -> StringTransformerSymbolReferenceAbsStx:
        return StringTransformerSymbolReferenceAbsStx(self.name)


class StringTransformerPrimitiveSymbolContext(StringTransformerSymbolContext):
    def __init__(self,
                 name: str,
                 primitive: StringTransformer,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         StringTransformerSymbolValueContext.of_primitive(primitive, definition_source))
        self._primitive = primitive

    @property
    def primitive(self) -> StringTransformer:
        return self._primitive


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringTransformerSymbolValueContext.of_primitive(
    IdentityStringTransformer()
)
