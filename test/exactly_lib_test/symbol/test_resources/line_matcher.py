from typing import Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_utils.matcher.impls import sdv_components, constant, ddv_components
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine, GenericLineMatcherSdv, \
    LineMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage, symbol_utils
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolValueContext, \
    ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def arbitrary_sdv() -> LineMatcherStv:
    return LineMatcherStv(
        sdv_components.matcher_sdv_from_constant_primitive(constant.MatcherWithConstantResult(True))
    )


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


def successful_matcher_with_validation(validator: DdvValidator):
    return LineMatcherStv(
        matchers.sdv_from_primitive_value(
            matchers.MatcherWithConstantResult(True),
            (),
            validator,
        )
    )


def stv_from_primitive_value(
        primitive_value: MatcherWTraceAndNegation[LineMatcherLine] = matchers.MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = constant_success_validator(),
) -> LineMatcherStv:
    return LineMatcherStv(
        matchers.sdv_from_primitive_value(
            primitive_value,
            references,
            validator,
        )
    )


def sdv_from_primitive_value(
        primitive_value: MatcherWTraceAndNegation[LineMatcherLine] = matchers.MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = constant_success_validator(),
) -> GenericLineMatcherSdv:
    return matchers.sdv_from_primitive_value(
        primitive_value,
        references,
        validator,
    )


def sdtv_of_unconditionally_matching_matcher() -> LineMatcherStv:
    return LineMatcherStv(matchers.sdv_of_unconditionally_matching_matcher())


def ddv_of_unconditionally_matching_matcher() -> LineMatcherDdv:
    return ddv_components.MatcherDdvFromConstantPrimitive(
        constant.MatcherWithConstantResult(False)
    )


class LineMatcherSymbolValueContext(LogicSymbolValueContext[LineMatcherStv]):
    def __init__(self,
                 sdv: LineMatcherStv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_generic(sdv: GenericLineMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext(LineMatcherStv(sdv),
                                             definition_source)

    @staticmethod
    def of_primitive(primitive: LineMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext.of_generic(matchers.sdv_from_primitive_value(primitive),
                                                        definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                          definition_source)

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_line_matcher_reference_to__ref(symbol_name)

    @property
    def container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def container__of_builtin(self) -> SymbolContainer:
        return symbol_utils.container_of_builtin(self.sdtv)


class LineMatcherSymbolContext(LogicTypeSymbolContext[LineMatcherStv]):
    def __init__(self,
                 name: str,
                 value: LineMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str,
                sdtv: LineMatcherStv,
                definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                ) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext(sdtv, definition_source)
        )

    @staticmethod
    def of_generic(name: str,
                   sdv: GenericLineMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext.of_generic(sdv, definition_source)
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


ARBITRARY_SYMBOL_VALUE_CONTEXT = LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
