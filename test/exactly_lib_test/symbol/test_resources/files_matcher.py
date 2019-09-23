from typing import Sequence, Optional

from exactly_lib.symbol import symbol_usage as su
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver, FilesMatcherModel, \
    FilesMatcherValue, FilesMatcherConstructor, FilesMatcher
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherTestImpl(FilesMatcher):
    def __init__(self,
                 result: bool = True):
        self._result = result

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def negation(self) -> FilesMatcher:
        return FilesMatcherTestImpl(not self._result)

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        if self._result:
            return None
        else:
            return err_msg_resolvers.constant('test impl with constant ' + str(self._result))


class FilesMatcherValueConstantTestImpl(FilesMatcherValue):
    def __init__(self,
                 constant: FilesMatcherConstructor,
                 ):
        self._constant = constant

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FilesMatcherConstructor:
        return self._constant


def constant_value(matcher: FilesMatcher) -> FilesMatcherValue:
    return FilesMatcherValueConstantTestImpl(
        files_matchers.ConstantConstructor(
            matcher
        )
    )


def value_with_result(result: bool) -> FilesMatcherValue:
    return FilesMatcherValueConstantTestImpl(
        files_matchers.ConstantConstructor(
            FilesMatcherTestImpl(result)
        )
    )


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
        return value_with_result(self._resolved_value)


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


def is_reference_to_files_matcher__ref(name_of_matcher: str) -> ValueAssertion[su.SymbolReference]:
    return asrt_sym_usage.matches_reference__ref(asrt.equals(name_of_matcher),
                                                 IS_FILES_MATCHER_REFERENCE_RESTRICTION)
