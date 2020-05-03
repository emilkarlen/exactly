from typing import Sequence

from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_utils.matcher.impls import sdv_components, constant, ddv_components
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine, GenericLineMatcherSdv, \
    LineMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolValueContext
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
    @staticmethod
    def of_generic(sdv: GenericLineMatcherSdv) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext(LineMatcherStv(sdv))

    @staticmethod
    def of_primitive(primitive: LineMatcher) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext.of_generic(matchers.sdv_from_primitive_value(primitive))

    @staticmethod
    def of_primitive_constant(result: bool) -> 'LineMatcherSymbolValueContext':
        return LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_line_matcher_reference_to__ref(symbol_name)


class LineMatcherSymbolContext(LogicTypeSymbolContext[LineMatcherStv]):
    def __init__(self,
                 name: str,
                 value: LineMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str, sdtv: LineMatcherStv) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext(sdtv)
        )

    @staticmethod
    def of_generic(name: str, sdv: GenericLineMatcherSdv) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext.of_generic(sdv)
        )

    @staticmethod
    def of_primitive(name: str, primitive: LineMatcher) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherSymbolValueContext.of_primitive(primitive)
        )

    @staticmethod
    def of_primitive_constant(name: str, result: bool) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext.of_primitive(name,
                                                     constant.MatcherWithConstantResult(result))


ARBITRARY_SYMBOL_VALUE_CONTEXT = LineMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
