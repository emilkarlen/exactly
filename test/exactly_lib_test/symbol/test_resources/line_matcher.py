from typing import Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_utils.matcher.impls import constant, ddv_components
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine, LineMatcherSdv, \
    LineMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION, \
    MatcherSymbolValueContext, MatcherTypeSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_LINE_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.LINE_MATCHER)


def is_line_matcher_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_LINE_MATCHER_REFERENCE_RESTRICTION)


def is_line_matcher_reference_to__ref(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                         IS_LINE_MATCHER_REFERENCE_RESTRICTION)
    )


def successful_matcher_with_validation(validator: DdvValidator) -> LineMatcherSdv:
    return matchers.sdv_from_primitive_value(
        matchers.MatcherWithConstantResult(True),
        (),
        validator,
    )


def sdv_from_primitive_value(
        primitive_value: MatcherWTraceAndNegation[LineMatcherLine] = matchers.MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = constant_success_validator(),
) -> LineMatcherSdv:
    return matchers.sdv_from_primitive_value(
        primitive_value,
        references,
        validator,
    )


def ddv_of_unconditionally_matching_matcher() -> LineMatcherDdv:
    return ddv_components.MatcherDdvFromConstantPrimitive(
        constant.MatcherWithConstantResult(False)
    )


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
        return LineMatcherSymbolValueContext.of_sdv(matchers.sdv_from_primitive_value(primitive),
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

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_line_matcher_reference_to__ref(symbol_name)


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


ARBITRARY_SYMBOL_VALUE_CONTEXT = LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
