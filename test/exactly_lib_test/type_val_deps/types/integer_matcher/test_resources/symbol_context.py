from typing import Optional

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.integer_matcher import IntegerMatcherSdv
from exactly_lib.type_val_prims.matcher.integer_matcher import IntegerMatcher
from exactly_lib_test.impls.types.integer_matcher.test_resources.argument_building import IntegerMatcherArg
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import \
    IntegerMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.references import \
    is_reference_to_integer_matcher
from exactly_lib_test.type_val_deps.types.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext


class IntegerMatcherSymbolValueContext(MatcherSymbolValueContext[int]):
    def __init__(self,
                 sdv: IntegerMatcherSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: IntegerMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'IntegerMatcherSymbolValueContext':
        return IntegerMatcherSymbolValueContext(sdv, definition_source)

    @staticmethod
    def of_primitive(primitive: IntegerMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'IntegerMatcherSymbolValueContext':
        return IntegerMatcherSymbolValueContext.of_sdv(
            sdv_ddv.sdv_from_primitive_value(primitive),
            definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'IntegerMatcherSymbolValueContext':
        return IntegerMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                             definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'IntegerMatcherSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.INTEGER_MATCHER

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_integer_matcher(symbol_name)


class IntegerMatcherSymbolContext(MatcherTypeSymbolContext[int]):
    def __init__(self,
                 name: str,
                 value: IntegerMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str,
               sdv: IntegerMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'IntegerMatcherSymbolContext':
        return IntegerMatcherSymbolContext(
            name,
            IntegerMatcherSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: IntegerMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'IntegerMatcherSymbolContext':
        return IntegerMatcherSymbolContext(
            name,
            IntegerMatcherSymbolValueContext.of_primitive(primitive, definition_source)
        )

    @staticmethod
    def of_primitive_constant(name: str,
                              result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'IntegerMatcherSymbolContext':
        return IntegerMatcherSymbolContext.of_primitive(name,
                                                        constant.MatcherWithConstantResult(result),
                                                        definition_source)

    @staticmethod
    def of_arbitrary_value(name: str) -> 'IntegerMatcherSymbolContext':
        return IntegerMatcherSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def argument(self) -> IntegerMatcherArg:
        return matcher_argument.SymbolReferenceWReferenceSyntax(self.name)

    @property
    def abstract_syntax(self) -> IntegerMatcherSymbolReferenceAbsStx:
        return IntegerMatcherSymbolReferenceAbsStx(self.name)


class IntegerMatcherSymbolContextOfPrimitiveConstant(IntegerMatcherSymbolContext):
    def __init__(self,
                 name: str,
                 result: bool,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         IntegerMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                                       definition_source))
        self._result = result

    @property
    def result_value(self) -> bool:
        return self._result


ARBITRARY_SYMBOL_VALUE_CONTEXT = IntegerMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
