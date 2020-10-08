from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.integer_matcher import IntegerMatcher, IntegerMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION, \
    MatcherSymbolValueContext, MatcherTypeSymbolContext
from exactly_lib_test.test_case_utils.integer_matcher.test_resources.argument_building import IntegerMatcherArg
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_INTEGER_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.INTEGER_MATCHER)


def is_reference_to_integer_matcher__usage(symbol_name: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_INTEGER_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_integer_matcher(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                         IS_INTEGER_MATCHER_REFERENCE_RESTRICTION)
    )


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
        return IntegerMatcherSymbolValueContext.of_sdv(matchers.sdv_from_primitive_value(primitive),
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

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
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