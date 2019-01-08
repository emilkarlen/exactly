from typing import Sequence, Optional

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, Environment, FilesMatcherModel, FilesMatcherValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherValueTestImpl(FilesMatcherValue):
    def __init__(self,
                 resolved_value: bool = True):
        self._resolved_value = resolved_value

    @property
    def negation(self) -> FilesMatcherValue:
        return FilesMatcherValueTestImpl(not self._resolved_value)

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        if self._resolved_value:
            return None
        else:
            return ConstantErrorMessageResolver('test impl with constant ' + str(self._resolved_value))


class FilesMatcherResolverConstantTestImpl(FilesMatcherResolver):
    def __init__(self,
                 resolved_value: bool = True,
                 references: Sequence[SymbolReference] = (),
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._resolved_value = resolved_value
        self._references = list(references)
        self._validator = validator

    @property
    def resolved_value(self) -> bool:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return FilesMatcherValueTestImpl(self._resolved_value)


class FilesMatcherResolverConstantValueTestImpl(FilesMatcherResolver):
    def __init__(self,
                 resolved_value: FilesMatcherValue,
                 references: Sequence[SymbolReference] = (),
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        self._resolved_value = resolved_value
        self._references = list(references)
        self._validator = validator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return self._resolved_value


IS_FILES_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILES_MATCHER)


def is_reference_to_files_matcher(name_of_matcher: str) -> ValueAssertion[su.SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(name_of_matcher),
                                            IS_FILES_MATCHER_REFERENCE_RESTRICTION)
