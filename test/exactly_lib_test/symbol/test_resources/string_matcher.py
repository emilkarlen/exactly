from typing import Sequence

from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.string_matcher import StringMatcher, GenericStringMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def arbitrary_sdv() -> StringMatcherSdv:
    return string_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(True))


def string_matcher_sdv_constant_test_impl(resolved_value: StringMatcher,
                                          references: Sequence[SymbolReference] = (),
                                          validator: DdvValidator = ddv_validation.ConstantDdvValidator(),
                                          ) -> StringMatcherSdv:
    return StringMatcherSdv(
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


class StringMatcherSymbolContext(SdvSymbolContext[StringMatcherSdv]):
    def __init__(self,
                 name: str,
                 sdv: StringMatcherSdv):
        super().__init__(name)
        self._sdv = sdv

    @staticmethod
    def of_generic(name: str, sdv: GenericStringMatcherSdv) -> 'StringMatcherSymbolContext':
        return StringMatcherSymbolContext(
            name,
            StringMatcherSdv(sdv)
        )

    @property
    def sdv(self) -> StringMatcherSdv:
        return self._sdv

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_string_matcher__ref(self.name)
