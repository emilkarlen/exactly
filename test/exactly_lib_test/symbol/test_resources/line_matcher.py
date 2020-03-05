from typing import Sequence

from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_utils.matcher.impls import sdv_components, constant, ddv_components
from exactly_lib.type_system.logic.line_matcher import LineMatcherDdv, LineMatcherLine, GenericLineMatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
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


def sdv_of_unconditionally_matching_matcher() -> LineMatcherStv:
    return LineMatcherStv(matchers.sdv_of_unconditionally_matching_matcher())


def ddv_of_unconditionally_matching_matcher() -> LineMatcherDdv:
    return ddv_components.MatcherDdvFromConstantPrimitive(
        constant.MatcherWithConstantResult(False)
    )


class LineMatcherSymbolContext(SdvSymbolContext[LineMatcherStv]):
    def __init__(self,
                 name: str,
                 stv: LineMatcherStv,
                 ):
        super().__init__(name)
        self._stv = stv

    @staticmethod
    def of_generic(name: str, sdv: GenericLineMatcherSdv) -> 'LineMatcherSymbolContext':
        return LineMatcherSymbolContext(
            name,
            LineMatcherStv(sdv)
        )

    @property
    def sdtv(self) -> LineMatcherStv:
        return self._stv

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_line_matcher_reference_to__ref(self.name)
