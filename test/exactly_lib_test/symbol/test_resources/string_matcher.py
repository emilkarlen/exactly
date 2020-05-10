from typing import Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.logic.string_matcher import StringMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage, SymbolContainer
from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.string_matcher import StringMatcher, GenericStringMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage, symbol_utils
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolValueContext, \
    ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def arbitrary_sdv() -> StringMatcherStv:
    return string_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(True))


def string_matcher_sdv_constant_test_impl(resolved_value: StringMatcher,
                                          references: Sequence[SymbolReference] = (),
                                          validator: DdvValidator = ddv_validation.ConstantDdvValidator(),
                                          ) -> StringMatcherStv:
    return StringMatcherStv(
        matchers.MatcherSdvOfConstantDdvTestImpl(
            matchers.MatcherDdvOfConstantMatcherTestImpl(
                resolved_value,
                validator,
            ),
            references,
        )
    )


IS_STRING_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.STRING_MATCHER)


def is_reference_to_string_matcher(name_of_matcher: str) -> ValueAssertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_STRING_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_string_matcher__ref(name_of_matcher: str
                                        ) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                         IS_STRING_MATCHER_REFERENCE_RESTRICTION)
    )


class StringMatcherSymbolValueContext(LogicSymbolValueContext[StringMatcherStv]):
    def __init__(self,
                 sdv: StringMatcherStv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_generic(sdv: GenericStringMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'StringMatcherSymbolValueContext':
        return StringMatcherSymbolValueContext(StringMatcherStv(sdv),
                                               definition_source)

    @staticmethod
    def of_primitive(primitive: StringMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'StringMatcherSymbolValueContext':
        return StringMatcherSymbolValueContext.of_generic(matchers.sdv_from_primitive_value(primitive),
                                                          definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'StringMatcherSymbolValueContext':
        return StringMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                            definition_source)

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_string_matcher__ref(symbol_name)

    @property
    def container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def container__of_builtin(self) -> SymbolContainer:
        return symbol_utils.container_of_builtin(self.sdtv)


class StringMatcherSymbolContext(LogicTypeSymbolContext[StringMatcherStv]):
    def __init__(self,
                 name: str,
                 value: StringMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str,
                sdtv: StringMatcherStv,
                definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                ) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext(
            name,
            StringMatcherSymbolValueContext(sdtv, definition_source)
        )

    @staticmethod
    def of_sdv(name: str,
               sdv: GenericStringMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext(
            name,
            StringMatcherSymbolValueContext.of_generic(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: StringMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext(
            name,
            StringMatcherSymbolValueContext.of_primitive(primitive, definition_source)
        )

    @staticmethod
    def of_primitive_constant(name: str,
                              result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext.of_primitive(name,
                                                       constant.MatcherWithConstantResult(result),
                                                       definition_source)


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
