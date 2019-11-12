from typing import Sequence, Callable

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv
from exactly_lib.type_system.logic.string_matcher_ddvs import StringMatcherConstantDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ResolverSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import string_matchers
from exactly_lib_test.type_system.logic.test_resources.string_matchers import StringMatcherDdvFromPartsTestImpl


def arbitrary_resolver() -> StringMatcherResolver:
    return StringMatcherResolverConstantTestImpl(string_matchers.StringMatcherConstant(None))


class StringMatcherResolverConstantTestImpl(StringMatcherResolver):
    def __init__(self,
                 resolved_value: StringMatcher,
                 references: Sequence[SymbolReference] = (),
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._resolved_value = resolved_value
        self._references = list(references)
        self._validator = validator

    @property
    def resolved_value(self) -> StringMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return StringMatcherConstantDdv(self._resolved_value)


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


class StringMatcherSymbolContext(ResolverSymbolContext[StringMatcherResolver]):
    def __init__(self,
                 name: str,
                 resolver: StringMatcherResolver):
        super().__init__(name)
        self._resolver = resolver

    @property
    def resolver(self) -> StringMatcherResolver:
        return self._resolver

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_string_matcher__ref(self.name)


class StringMatcherResolverFromPartsTestImpl(StringMatcherResolver):
    def __init__(self,
                 structure: StructureRenderer,
                 references: Sequence[SymbolReference],
                 validator: PreOrPostSdsValidator,
                 matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], StringMatcher]):
        self._structure = structure
        self._matcher = matcher
        self._validator = validator
        self._references = references

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        def get_matcher(tcds: HomeAndSds) -> StringMatcher:
            environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            return self._matcher(environment)

        return StringMatcherDdvFromPartsTestImpl(self._structure,
                                                 get_matcher)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def __str__(self):
        return str(type(self))
