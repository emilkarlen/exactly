from typing import Sequence, Callable, Generic

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.logic.matcher import MatcherSdv, MODEL
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv
from exactly_lib.type_system.logic.string_matcher import StringMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.string_matchers import MatcherDdvFromPartsTestImpl


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


def is_reference_to_string_matcher(name_of_matcher: str) -> ValueAssertion[su.SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_STRING_MATCHER_REFERENCE_RESTRICTION)


def is_reference_to_string_matcher__ref(name_of_matcher: str) -> ValueAssertion[su.SymbolReference]:
    return asrt.is_instance_with(
        su.SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                         IS_STRING_MATCHER_REFERENCE_RESTRICTION)
    )


class StringMatcherSymbolContext(SdvSymbolContext[StringMatcherSdv]):
    def __init__(self,
                 name: str,
                 sdv: StringMatcherSdv):
        super().__init__(name)
        self._sdv = sdv

    @property
    def sdv(self) -> StringMatcherSdv:
        return self._sdv

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_string_matcher__ref(self.name)


def matcher_sdv_from_parts_test_impl(
        structure: StructureRenderer,
        references: Sequence[SymbolReference],
        matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], MatcherWTraceAndNegation[MODEL]],
        validator: DdvValidator = ddv_validation.constant_success_validator(),
) -> StringMatcherSdv:
    return StringMatcherSdv(
        MatcherSdvFromPartsTestImpl(structure,
                                    references,
                                    matcher,
                                    validator)
    )


class MatcherSdvFromPartsTestImpl(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self,
                 structure: StructureRenderer,
                 references: Sequence[SymbolReference],
                 matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], MatcherWTraceAndNegation[MODEL]],
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 ):
        self._structure = structure
        self._references = references
        self._validator = validator
        self._matcher = matcher

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        def get_matcher(tcds: Tcds) -> StringMatcher:
            environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            return self._matcher(environment)

        return MatcherDdvFromPartsTestImpl(self._structure,
                                           get_matcher,
                                           self._validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))
