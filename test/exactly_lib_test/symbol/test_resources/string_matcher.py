from typing import Sequence, Callable

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherDdv
from exactly_lib.type_system.logic.string_matcher_ddvs import StringMatcherConstantDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import string_matchers
from exactly_lib_test.type_system.logic.test_resources.string_matchers import StringMatcherDdvFromPartsTestImpl


def arbitrary_sdv() -> StringMatcherSdv:
    return StringMatcherSdvConstantTestImpl(string_matchers.StringMatcherConstant(None))


class StringMatcherSdvConstantTestImpl(StringMatcherSdv):
    def __init__(self,
                 resolved_value: StringMatcher,
                 references: Sequence[SymbolReference] = (),
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator()):
        self._resolved_value = resolved_value
        self._references = list(references)
        self._validator = validator

    @property
    def resolved_value(self) -> StringMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        return StringMatcherConstantDdv(self._resolved_value,
                                        self._validator)


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


class StringMatcherSdvFromPartsTestImpl(StringMatcherSdv):
    def __init__(self,
                 structure: StructureRenderer,
                 references: Sequence[SymbolReference],
                 matcher: Callable[[PathResolvingEnvironmentPreOrPostSds], StringMatcher],
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 ):
        self._structure = structure
        self._references = references
        self._validator = validator
        self._matcher = matcher

    def resolve(self, symbols: SymbolTable) -> StringMatcherDdv:
        def get_matcher(tcds: Tcds) -> StringMatcher:
            environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbols)
            return self._matcher(environment)

        return StringMatcherDdvFromPartsTestImpl(self._structure,
                                                 get_matcher,
                                                 self._validator)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))
