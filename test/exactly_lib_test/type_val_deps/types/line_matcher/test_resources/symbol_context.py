from typing import Optional

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine, LineMatcher
from exactly_lib_test.impls.types.line_matcher.test_resources import arguments_building as args
from exactly_lib_test.impls.types.line_matcher.test_resources.arguments_building import LineMatcherArg
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.abstract_syntax import \
    LineMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.references import is_reference_to_line_matcher
from exactly_lib_test.type_val_deps.types.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext


class LineMatcherSymbolValueContext(MatcherSymbolValueContext[LineMatcherLine]):
    def __init__(self,
                 sdv: LineMatcherSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: LineMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext(sdv,
                                             definition_source)

    @staticmethod
    def of_primitive(primitive: LineMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext.of_sdv(
            sdv_ddv.sdv_from_primitive_value(primitive),
            definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                          definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'LineMatcherSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.LINE_MATCHER

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_line_matcher(symbol_name)


class LineMatcherSymbolContext(MatcherTypeSymbolContext[LineMatcherLine]):
    def __init__(self,
                 name: str,
                 value: LineMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str,
               sdv: LineMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: LineMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext.of_primitive(primitive, definition_source)
        )

    @staticmethod
    def of_primitive_constant(name: str,
                              result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext.of_primitive(name,
                                                     constant.MatcherWithConstantResult(result),
                                                     definition_source)

    @staticmethod
    def of_arbitrary_value(name: str) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def argument(self) -> LineMatcherArg:
        return args.SymbolReferenceWReferenceSyntax(self.name)

    @property
    def abstract_syntax(self) -> LineMatcherSymbolReferenceAbsStx:
        return LineMatcherSymbolReferenceAbsStx(self.name)


class LineMatcherSymbolContextOfPrimitiveConstant(LineMatcherSymbolContext):
    def __init__(self,
                 name: str,
                 result: bool,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                                    definition_source))
        self._result = result

    @property
    def result_value(self) -> bool:
        return self._result


ARBITRARY_SYMBOL_VALUE_CONTEXT = LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
