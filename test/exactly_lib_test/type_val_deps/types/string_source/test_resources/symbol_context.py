from typing import Optional

from exactly_lib.impls.types.string_source import sdvs
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.full_deps.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import \
    StringSourceSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.references import \
    IS_STRING_SOURCE_OR_STRING_REFERENCE_RESTRICTION


def is_reference_to_string_source__usage(name_of_matcher: str) -> Assertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_STRING_SOURCE_OR_STRING_REFERENCE_RESTRICTION)


def is_reference_to_string_source(name_of_matcher: str) -> Assertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                         IS_STRING_SOURCE_OR_STRING_REFERENCE_RESTRICTION)
    )


class StringSourceSymbolValueContext(LogicSymbolValueContext[StringSource]):
    def __init__(self,
                 sdv: StringSourceSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: StringSourceSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringSourceSymbolValueContext':
        return StringSourceSymbolValueContext(sdv,
                                              definition_source)

    @staticmethod
    def of_primitive_constant(contents: str,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'StringSourceSymbolValueContext':
        return StringSourceSymbolValueContext.of_sdv(
            sdvs.ConstantStringStringSourceSdv(string_sdvs.str_constant(contents)),
            definition_source,
        )

    @staticmethod
    def of_arbitrary_value() -> 'StringSourceSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_SOURCE

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_string_source(symbol_name)

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_SOURCE


class StringSourceSymbolContext(LogicTypeSymbolContext[StringSource]):
    def __init__(self,
                 name: str,
                 value: StringSourceSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: StringSourceSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringSourceSymbolContext':
        return StringSourceSymbolContext(
            name,
            StringSourceSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive_constant(name: str,
                              contents: str,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'StringSourceSymbolContext':
        return StringSourceSymbolContext(
            name,
            StringSourceSymbolValueContext.of_primitive_constant(contents,
                                                                 definition_source),
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'StringSourceSymbolContext':
        return StringSourceSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> LogicSymbolValueContext[StringSourceSdv]:
        return self._value

    @property
    def abstract_syntax(self) -> StringSourceSymbolReferenceAbsStx:
        return StringSourceSymbolReferenceAbsStx(self.name)

    @property
    def reference_sdv(self) -> StringSourceSdv:
        raise ValueType('unsupported - would like to remove this method from base class')
        # since implies too many dependencies


class StringSourceSymbolContextOfPrimitiveConstant(StringSourceSymbolContext):
    def __init__(self,
                 name: str,
                 contents: str,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         StringSourceSymbolValueContext.of_primitive_constant(
                             contents,
                             definition_source)
                         )
        self._contents = contents

    @property
    def contents_str(self) -> str:
        return self._contents


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringSourceSymbolValueContext.of_primitive_constant(
    'arbitrary contents'
)
