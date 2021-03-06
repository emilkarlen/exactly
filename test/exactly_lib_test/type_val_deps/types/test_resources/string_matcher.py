from typing import Sequence, Optional

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.matcher.string_matcher import StringMatcher
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as args
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building2 import StringMatcherArg
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import \
    StringMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext


def string_matcher_sdv_constant_test_impl(resolved_value: StringMatcher,
                                          references: Sequence[SymbolReference] = (),
                                          validator: DdvValidator = ddv_validation.ConstantDdvValidator(),
                                          ) -> StringMatcherSdv:
    return sdv_ddv.MatcherSdvOfConstantDdvTestImpl(
        sdv_ddv.MatcherDdvOfConstantMatcherTestImpl(
            resolved_value,
            validator,
        ),
        references,
    )


IS_STRING_MATCHER_REFERENCE_RESTRICTION = is_reference_restrictions__value_type((ValueType.STRING_MATCHER,))


def is_reference_to_string_matcher__usage(name_of_matcher: str) -> Assertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_STRING_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_string_matcher(name_of_matcher: str) -> Assertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                         IS_STRING_MATCHER_REFERENCE_RESTRICTION)
    )


class StringMatcherSymbolValueContext(MatcherSymbolValueContext[StringSource]):
    def __init__(self,
                 sdv: StringMatcherSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: StringMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringMatcherSymbolValueContext':
        return StringMatcherSymbolValueContext(sdv,
                                               definition_source)

    @staticmethod
    def of_primitive(primitive: StringMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'StringMatcherSymbolValueContext':
        return StringMatcherSymbolValueContext.of_sdv(
            sdv_ddv.sdv_from_primitive_value(primitive),
            definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'StringMatcherSymbolValueContext':
        return StringMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                            definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'StringMatcherSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_string_matcher(symbol_name)

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_MATCHER


class StringMatcherSymbolContext(MatcherTypeSymbolContext[StringSource]):
    def __init__(self,
                 name: str,
                 value: StringMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str,
               sdv: StringMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext(
            name,
            StringMatcherSymbolValueContext.of_sdv(sdv, definition_source)
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

    @staticmethod
    def of_arbitrary_value(name: str) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def argument(self) -> StringMatcherArg:
        return args.SymbolReferenceWReferenceSyntax(self.name)

    @property
    def abstract_syntax(self) -> StringMatcherSymbolReferenceAbsStx:
        return StringMatcherSymbolReferenceAbsStx(self.name)


class StringMatcherSymbolContextOfPrimitiveConstant(StringMatcherSymbolContext):
    def __init__(self,
                 name: str,
                 result: bool,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         StringMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                                      definition_source))
        self._result = result

    @property
    def result_value(self) -> bool:
        return self._result


ARBITRARY_SYMBOL_VALUE_CONTEXT = StringMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
